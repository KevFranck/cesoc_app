"""Fenetre principale du client desktop."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QMenu,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
)

from client.app.core.config import get_client_settings
from client.app.services.api_client import ApiClient
from client.app.services.app_launcher import AppLauncher
from client.app.services.session_store import CurrentSession
from client.app.services.workspace_service import WorkspaceService
from client.app.printers.windows_print_monitor import WindowsPrintMonitor
from client.app.session_tracker.timer import SessionTimer
from client.app.ui.resources import get_app_icon
from client.app.ui.views.compact_session_view import CompactSessionView
from client.app.ui.views.login_view import LoginView
from client.app.ui.views.mini_session_view import MiniSessionView


class MainWindow(QMainWindow):
    """Fenetre principale du MVP desktop."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_client_settings()
        self.ui_settings = QSettings("CESOC", "ClientDesktop")
        self.api_client = ApiClient(self.settings.client_api_base_url)
        self.app_launcher = AppLauncher(self.settings.client_word_executable)
        self.workspace_service = WorkspaceService(self.settings.client_workspace_root)
        self.print_monitor = WindowsPrintMonitor(
            interval_ms=self.settings.client_print_monitor_interval_ms,
            parent=self,
        )
        self.current_session: CurrentSession | None = None
        self.session_timer = SessionTimer(self)
        self.session_timer.tick.connect(self._update_timer_display)
        self.session_timer.warning.connect(self._handle_session_warning)
        self.session_timer.expired.connect(self._expire_session)
        self.print_monitor.job_detected.connect(self._handle_detected_print_job)
        self.print_monitor.monitor_error.connect(self._handle_print_monitor_error)
        self._warning_thresholds_seen: set[int] = set()
        self._tray_message_shown = False

        self.setWindowTitle(self.settings.client_app_name)
        self.app_icon = get_app_icon()
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        self.stack = QStackedWidget()
        self.login_view = LoginView(self.handle_login, self.handle_register)
        self.mini_view = MiniSessionView(
            on_expand=self.show_compact_panel,
            on_logout=self.handle_logout,
        )
        self.compact_view = CompactSessionView(
            on_refresh=self.load_dashboard_data,
            on_hide=self.minimize_to_taskbar,
            on_change_password=self.handle_change_password,
            on_logout=self.handle_logout,
            on_open_browser=self.handle_open_browser,
            on_open_word=self.handle_open_word,
            on_open_workspace=self.handle_open_workspace,
        )
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.mini_view)
        self.stack.addWidget(self.compact_view)
        self.setCentralWidget(self.stack)
        self._tray_icon = self._create_tray_icon()

        self._enter_login_mode()
        self.bootstrap()

    def bootstrap(self) -> None:
        """Charge les donnees initiales."""
        try:
            workstations = self.api_client.list_workstations()
        except RuntimeError as exc:
            self.login_view.set_feedback(str(exc), level="danger")
            return

        self.login_view.set_workstations(
            [item["name"] for item in workstations],
            default_name=self.settings.client_default_workstation,
        )
        self.login_view.clear_feedback()
        self.login_view.focus_identifier()

    def handle_login(self, email: str, password: str, workstation_name: str) -> None:
        """Connecte l'utilisateur."""
        self.login_view.set_busy(True)
        try:
            payload = self.api_client.login(email, password, workstation_name)
        except RuntimeError as exc:
            self.login_view.set_feedback(str(exc), level="danger")
            self.login_view.set_busy(False)
            self.login_view.focus_identifier()
            return
        finally:
            self.login_view.set_busy(False)

        user = payload["user"]
        session = payload["session"]
        if user["role"] == "admin":
            try:
                self.api_client.close_session(session["id"])
            except RuntimeError:
                pass
            self.login_view.set_feedback("Ce compte n'est pas autorise sur ce poste.", level="danger")
            self.login_view.focus_identifier()
            return

        started_at = datetime.fromisoformat(session["started_at"])
        workspace_path = self.workspace_service.ensure_session_workspace(
            email=user["email"],
            workstation_name=session["workstation"]["name"],
            started_at=started_at,
        )
        self.current_session = CurrentSession(
            session_id=session["id"],
            email=user["email"],
            user_name=f"{user['first_name']} {user['last_name']}",
            workstation_name=session["workstation"]["name"],
            started_at=started_at,
            workspace_path=workspace_path,
        )

        self.compact_view.set_session_header(
            self.current_session.user_name,
            self.current_session.email,
            self.current_session.workstation_name,
        )
        self.mini_view.set_session_header(
            self.current_session.user_name,
            self.current_session.workstation_name,
        )
        self.compact_view.set_workspace_path(str(self.current_session.workspace_path))
        self.compact_view.set_print_quota(0, 0, 0)
        self.mini_view.set_print_quota(0, 0)
        self.compact_view.clear_status_message()
        self._warning_thresholds_seen = set()
        self.session_timer.start(
            started_at=self.current_session.started_at,
            limit_minutes=self.settings.client_session_limit_minutes,
            warning_thresholds=self.settings.session_warning_thresholds,
        )
        if self.settings.client_print_monitor_enabled:
            self.print_monitor.forget_processed_jobs()
            self.print_monitor.start()
        self.load_dashboard_data()
        self.stack.setCurrentWidget(self.compact_view)
        self._enter_compact_session_mode()
        self.show()
        self.raise_()
        self.activateWindow()

    def handle_register(self, email: str, first_name: str, last_name: str, password: str) -> None:
        """Cree un nouveau compte client."""
        self.login_view.set_busy(True)
        try:
            self.api_client.register(email, first_name, last_name, password)
        except RuntimeError as exc:
            self.login_view.set_feedback(str(exc), level="danger")
            return
        finally:
            self.login_view.set_busy(False)

        self.login_view.set_feedback(
            "Compte cree avec succes. Vous pouvez maintenant vous connecter.",
            level="success",
        )
        self.login_view.show_login_mode()
        self.login_view.password_input.clear()
        self.login_view.focus_identifier()

    def load_dashboard_data(self) -> None:
        """Recharge les donnees utiles au panneau utilisateur."""
        if not self.current_session:
            return

        try:
            quota = self.api_client.get_print_quota(self.current_session.email)
        except RuntimeError as exc:
            self._show_error(str(exc))
            return

        self.compact_view.set_print_quota(
            pages_used_today=int(quota.get("pages_used_today", 0)),
            remaining_quota=int(quota.get("remaining_quota", 0)),
            daily_quota=int(quota.get("daily_quota", 0)),
        )
        self.mini_view.set_print_quota(
            remaining_quota=int(quota.get("remaining_quota", 0)),
            daily_quota=int(quota.get("daily_quota", 0)),
        )

    def handle_open_browser(self) -> None:
        """Ouvre le navigateur autorise."""
        try:
            self.app_launcher.open_browser(self.settings.client_browser_home_url)
            self.compact_view.set_status_message(
                "Navigateur ouvert. Vous pouvez consulter le web dans votre session.",
                level="success",
            )
        except RuntimeError as exc:
            self._show_error(str(exc))

    def handle_open_word(self) -> None:
        """Ouvre Microsoft Word."""
        try:
            self.app_launcher.open_word()
            self._refresh_launcher_status("Microsoft Word a ete lance.")
        except RuntimeError as exc:
            self._show_error(str(exc))

    def handle_open_workspace(self) -> None:
        """Ouvre le dossier de travail."""
        if not self.current_session:
            return
        try:
            self.app_launcher.open_path(self.current_session.workspace_path)
            self._refresh_launcher_status("Le dossier de travail de la session a ete ouvert.")
        except RuntimeError as exc:
            self._show_error(str(exc))

    def handle_change_password(self) -> None:
        """Permet a l'utilisateur connecte de modifier son mot de passe."""
        if not self.current_session:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier le mot de passe")
        dialog.setModal(True)
        layout = QFormLayout(dialog)

        current_password_input = QLineEdit()
        current_password_input.setEchoMode(QLineEdit.Password)
        new_password_input = QLineEdit()
        new_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input = QLineEdit()
        confirm_password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Mot de passe actuel", current_password_input)
        layout.addRow("Nouveau mot de passe", new_password_input)
        layout.addRow("Confirmer", confirm_password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        current_password = current_password_input.text()
        new_password = new_password_input.text()
        confirm_password = confirm_password_input.text()

        if not current_password or not new_password:
            self._show_error("Veuillez renseigner le mot de passe actuel et le nouveau mot de passe.")
            return
        if new_password != confirm_password:
            self._show_error("La confirmation du nouveau mot de passe ne correspond pas.")
            return

        try:
            payload = self.api_client.change_password(
                self.current_session.email,
                current_password,
                new_password,
            )
        except RuntimeError as exc:
            self._show_error(str(exc))
            return

        self.compact_view.set_status_message(payload.get("message", "Mot de passe modifie."), level="success")
        self.compact_view.show_info("Mot de passe", payload.get("message", "Mot de passe modifie."))

    def handle_logout(self) -> None:
        """Ferme la session courante."""
        if not self.current_session:
            return
        if not self.compact_view.confirm_logout():
            return

        closed_processes = self.app_launcher.close_tracked_processes()
        try:
            self.api_client.close_session(self.current_session.session_id)
        except RuntimeError as exc:
            self._show_error(str(exc))
            return

        self.session_timer.stop()
        self.print_monitor.stop()
        self.current_session = None
        self.compact_view.set_workspace_path("-")
        self.compact_view.set_timer(0, 0, "00:00:00")
        self.compact_view.set_print_quota(0, 0, 0)
        self.mini_view.set_print_quota(0, 0)
        if closed_processes:
            self.compact_view.set_status_message(
                f"{closed_processes} application(s) lancee(s) par CESOC ont ete fermees.",
                level="neutral",
            )
        else:
            self.compact_view.clear_status_message()
        self.stack.setCurrentWidget(self.login_view)
        self._enter_login_mode()
        self.login_view.clear_feedback()
        self.login_view.show_login_mode()
        self.login_view.password_input.clear()
        self.login_view.focus_identifier()

    def _update_timer_display(
        self,
        elapsed_minutes: int,
        remaining_minutes: int,
        formatted_remaining: str,
    ) -> None:
        self.compact_view.set_timer(elapsed_minutes, remaining_minutes, formatted_remaining)
        self.mini_view.set_timer(formatted_remaining)

    def _expire_session(self) -> None:
        if not self.current_session:
            return

        self.compact_view.show_info(
            "Temps ecoule",
            "La duree de session configuree est atteinte. La session applicative va etre fermee.",
        )
        self._force_logout()

    def _handle_session_warning(self, threshold: int) -> None:
        if threshold in self._warning_thresholds_seen:
            return
        self._warning_thresholds_seen.add(threshold)

        if threshold <= 1:
            message = "Attention : il reste moins d'une minute avant la fin de la session."
        else:
            message = f"Attention : il reste environ {threshold} minutes avant la fin de la session."
        self.compact_view.set_status_message(message, level="warning")
        self.compact_view.show_info("Fin de session approchee", message)

    def _refresh_launcher_status(self, message: str) -> None:
        self.compact_view.set_status_message(message, level="success")

    def _force_logout(self) -> None:
        if not self.current_session:
            return

        closed_processes = self.app_launcher.close_tracked_processes()
        try:
            self.api_client.close_session(self.current_session.session_id)
        except RuntimeError as exc:
            self._show_error(str(exc))
            return

        self.session_timer.stop()
        self.print_monitor.stop()
        self.current_session = None
        self.compact_view.set_workspace_path("-")
        self.compact_view.set_timer(0, 0, "00:00:00")
        self.compact_view.set_print_quota(0, 0, 0)
        self.mini_view.set_print_quota(0, 0)
        if closed_processes:
            self.compact_view.set_status_message(
                f"{closed_processes} application(s) CESOC ont ete fermees automatiquement.",
                level="neutral",
            )
        else:
            self.compact_view.clear_status_message()
        self.stack.setCurrentWidget(self.login_view)
        self._enter_login_mode()
        self.login_view.clear_feedback()
        self.login_view.show_login_mode()
        self.login_view.password_input.clear()
        self.login_view.focus_identifier()

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Erreur", message)

    def _handle_detected_print_job(self, job: dict) -> None:
        """Traite un job d'impression detecte sur Windows."""
        if not self.current_session:
            return

        try:
            result = self.api_client.observe_print_job(
                email=self.current_session.email,
                workstation_name=self.current_session.workstation_name,
                pages=int(job.get("pages", 1)),
                printer_name=job.get("printer_name"),
                document_name=job.get("document_name"),
                spool_job_id=job.get("spool_job_id"),
                total_pages_seen=job.get("pages_total_seen"),
            )
        except RuntimeError as exc:
            self.compact_view.set_status_message(str(exc), level="danger")
            return

        if result.get("allowed"):
            if job.get("paused_once"):
                self.print_monitor.resume_job(
                    str(job.get("printer_name", "")),
                    int(job.get("spool_job_id", 0)),
                )
            self.compact_view.set_status_message(
                (
                    f"Impression autorisee sur {job.get('printer_name', 'imprimante inconnue')}. "
                    f"Il vous reste {int(result.get('remaining_quota', 0))} page(s) aujourd'hui."
                ),
                level="success",
            )
            self.load_dashboard_data()
            return

        printer_name = str(job.get("printer_name", ""))
        spool_job_id = int(job.get("spool_job_id", 0))
        cancelled = self.print_monitor.cancel_job(printer_name, spool_job_id)
        status_message = (
            (
                "Impression bloquee : votre quota quotidien de 10 pages est atteint. "
                "Vous ne pouvez plus imprimer aujourd'hui sur ce poste."
            )
            if cancelled
            else (
                "Votre quota quotidien de 10 pages est atteint. L'impression a ete detectee mais le blocage automatique a echoue. "
                "Veuillez demander de l'aide au personnel."
            )
        )
        self.compact_view.set_status_message(status_message, level="danger")
        self.compact_view.show_info("Impression", status_message)
        self.load_dashboard_data()

    def _handle_print_monitor_error(self, message: str) -> None:
        """Affiche une erreur non bloquante du watcher d'impression."""
        if self.current_session:
            self.compact_view.set_status_message(message, level="warning")

    def _enter_login_mode(self) -> None:
        self._tray_icon.hide()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.settings.client_login_kiosk_enabled)
        self.setWindowFlag(Qt.FramelessWindowHint, self.settings.client_login_kiosk_enabled)
        self.setMinimumSize(980, 620)
        self.setMaximumSize(16777215, 16777215)
        if self.settings.client_login_kiosk_enabled:
            self.showFullScreen()
        else:
            self._restore_window_geometry("login_geometry", (1120, 700), (980, 620))
            self.show()
        self.raise_()
        self.activateWindow()

    def _enter_compact_session_mode(self) -> None:
        self._tray_icon.hide()
        self.setWindowFlag(Qt.FramelessWindowHint, False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.showNormal()
        self._set_full_height_panel_geometry(width=420, minimum_width=390)
        self.show()

    def _enter_mini_mode(self) -> None:
        self._tray_icon.hide()
        self.setWindowFlag(Qt.FramelessWindowHint, False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.showNormal()
        self._restore_window_geometry("mini_geometry", (420, 74), (360, 68))
        self.show()

    def show_mini_panel(self) -> None:
        """Affiche la barre mini visible sur le bureau."""
        if not self.current_session:
            return
        self._save_current_geometry()
        self.stack.setCurrentWidget(self.mini_view)
        self._enter_mini_mode()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def show_compact_panel(self) -> None:
        """Restaure le panneau complet."""
        if not self.current_session:
            return
        self._save_current_geometry()
        self.stack.setCurrentWidget(self.compact_view)
        self._enter_compact_session_mode()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def hide_to_tray(self) -> None:
        """Masque le panneau compact dans la zone de notification."""
        if not self.current_session:
            return
        self._save_current_geometry()
        self.hide()
        if self._tray_icon.isVisible() and not self._tray_message_shown:
            self._tray_icon.showMessage(
                "CESOC",
                "La session continue en arriere-plan. Utilisez l'icone de notification pour rouvrir le panneau.",
                QSystemTrayIcon.Information,
                3000,
            )
            self._tray_message_shown = True

    def minimize_to_taskbar(self) -> None:
        """Minimise le panneau dans la barre des taches Windows."""
        if not self.current_session:
            return
        self.showMinimized()

    def show_from_tray(self) -> None:
        """Rouvre l'application depuis la zone de notification."""
        if self.current_session:
            self.show_compact_panel()
            return
        self.stack.setCurrentWidget(self.login_view)
        self._enter_login_mode()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Intercepte la fermeture pendant une session active."""
        if self.stack.currentWidget() is self.login_view:
            event.ignore()
            self._enter_login_mode()
            return
        if self.current_session:
            event.ignore()
            self.minimize_to_taskbar()
            return
        self._save_current_geometry()
        super().closeEvent(event)

    def moveEvent(self, event) -> None:  # type: ignore[override]
        self._save_current_geometry()
        super().moveEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        self._save_current_geometry()
        super().resizeEvent(event)

    def changeEvent(self, event) -> None:  # type: ignore[override]
        super().changeEvent(event)

    def _create_tray_icon(self) -> QSystemTrayIcon:
        """Cree l'icone de notification et son menu."""
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(
            self.app_icon if not self.app_icon.isNull() else self.style().standardIcon(QStyle.SP_ComputerIcon)
        )
        tray_icon.setToolTip("CESOC Client")

        menu = QMenu(self)
        show_action = menu.addAction("Afficher CESOC")
        show_action.triggered.connect(self.show_from_tray)

        hide_action = menu.addAction("Masquer le panneau")
        hide_action.triggered.connect(self.hide_to_tray)

        logout_action = menu.addAction("Terminer la session")
        logout_action.triggered.connect(self.handle_logout)

        menu.addSeparator()
        quit_action = menu.addAction("Quitter")
        quit_action.triggered.connect(self._quit_application)

        tray_icon.setContextMenu(menu)
        tray_icon.activated.connect(self._handle_tray_activation)
        tray_icon.show()
        return tray_icon

    def _handle_tray_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in {
            QSystemTrayIcon.Trigger,
            QSystemTrayIcon.DoubleClick,
        }:
            self.show_from_tray()

    def _quit_application(self) -> None:
        """Quitte l'application depuis la zone de notification."""
        if self.stack.currentWidget() is self.login_view:
            self._enter_login_mode()
            return
        if self.current_session:
            if not self.compact_view.confirm_logout():
                return
            self._force_logout()
        self._save_current_geometry()
        QApplication.instance().quit()

    def _restore_window_geometry(
        self,
        settings_key: str,
        default_size: tuple[int, int],
        minimum_size: tuple[int, int],
    ) -> None:
        self.setMinimumSize(*minimum_size)
        self.setMaximumSize(16777215, 16777215)
        geometry = self.ui_settings.value(settings_key)
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(*default_size)

    def _set_full_height_panel_geometry(self, width: int, minimum_width: int) -> None:
        screen = self.screen() or QApplication.primaryScreen()
        if not screen:
            self.resize(width, 720)
            return

        available = screen.availableGeometry()
        panel_width = min(width, available.width())
        self.setMinimumSize(min(minimum_width, panel_width), available.height())
        self.setMaximumSize(panel_width, available.height())
        self.setGeometry(
            available.right() - panel_width + 1,
            available.top(),
            panel_width,
            available.height(),
        )

    def _save_current_geometry(self) -> None:
        if not hasattr(self, "stack"):
            return
        current_view = self.stack.currentWidget()
        if current_view is self.login_view and self.settings.client_login_kiosk_enabled:
            return
        if current_view is self.compact_view:
            return
        if current_view is self.mini_view:
            key = "mini_geometry"
        else:
            key = "login_geometry"
        self.ui_settings.setValue(key, self.saveGeometry())


def run() -> int:
    """Lance la fenetre principale."""
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("CESOC Client")
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    window = MainWindow()
    return app.exec()
