"""Vue principale apres connexion."""

from collections.abc import Callable

from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DashboardView(QWidget):
    """Dashboard du poste."""

    def __init__(
        self,
        on_print: Callable[[int], None],
        on_refresh: Callable[[], None],
        on_logout: Callable[[], None],
        on_open_browser: Callable[[], None],
        on_open_word: Callable[[], None],
        on_open_workspace: Callable[[], None],
        on_open_pdf: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_print = on_print
        self._on_refresh = on_refresh
        self._on_logout = on_logout
        self._on_open_browser = on_open_browser
        self._on_open_word = on_open_word
        self._on_open_workspace = on_open_workspace
        self._on_open_pdf = on_open_pdf
        self._build_ui()

    def set_session_header(self, user_name: str, email: str, workstation_name: str) -> None:
        """Met a jour le resume de session."""
        self.user_value.setText(user_name)
        self.email_value.setText(email)
        self.workstation_value.setText(workstation_name)

    def set_timer(self, elapsed_minutes: int, remaining_minutes: int, formatted_remaining: str) -> None:
        """Affiche la progression de session."""
        self.elapsed_value.setText(f"{elapsed_minutes} min")
        self.remaining_value.setText(f"{remaining_minutes} min")
        self.countdown_value.setText(formatted_remaining)

    def set_workspace_path(self, workspace_path: str) -> None:
        """Affiche le dossier de travail."""
        self.workspace_value.setText(workspace_path)

    def set_status_message(self, message: str, level: str = "neutral") -> None:
        """Affiche un message de statut visible sur le dashboard."""
        colors = {
            "neutral": ("#eef3f0", "#37534c"),
            "warning": ("#fff3d9", "#8b5a00"),
            "danger": ("#fde4e1", "#8a2138"),
            "success": ("#e4f5ea", "#1c6441"),
        }
        background, foreground = colors.get(level, colors["neutral"])
        self.status_banner.setText(message)
        self.status_banner.setStyleSheet(
            f"background: {background}; color: {foreground}; border-radius: 10px; padding: 10px 12px; font-weight: 600;"
        )
        self.status_banner.show()

    def clear_status_message(self) -> None:
        """Masque le message de statut."""
        self.status_banner.hide()

    def set_launched_apps_count(self, count: int) -> None:
        """Affiche le nombre d'applications suivies par le client."""
        self.launched_apps_value.setText(str(count))

    def set_report(self, report: dict[str, str | int]) -> None:
        """Affiche les stats du jour."""
        self.report_connections.setText(str(report.get("total_connections", 0)))
        self.report_active.setText(str(report.get("active_sessions", 0)))
        self.report_minutes.setText(str(report.get("total_minutes_used", 0)))
        self.report_prints.setText(str(report.get("total_pages_printed", 0)))

    def set_active_sessions(self, sessions: list[dict[str, object]]) -> None:
        """Remplit le tableau des sessions actives."""
        self.sessions_table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            user = session["user"]
            workstation = session["workstation"]
            self.sessions_table.setItem(row, 0, QTableWidgetItem(str(user["email"])))
            self.sessions_table.setItem(
                row, 1, QTableWidgetItem(f"{user['first_name']} {user['last_name']}")
            )
            self.sessions_table.setItem(row, 2, QTableWidgetItem(str(workstation["name"])))
            self.sessions_table.setItem(row, 3, QTableWidgetItem(str(session["started_at"])))

        self.sessions_table.resizeColumnsToContents()

    def show_print_result(self, result: dict[str, object]) -> None:
        """Affiche le resultat d'une impression."""
        title = "Impression autorisee" if result.get("allowed") else "Impression bloquee"
        QMessageBox.information(self, title, str(result.get("message", "")))

    def ask_pdf_path(self, initial_dir: str) -> str | None:
        """Permet de choisir un PDF a ouvrir."""
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un PDF",
            initial_dir,
            "PDF Files (*.pdf)",
        )
        return selected_path or None

    def show_info(self, title: str, message: str) -> None:
        """Affiche une information utilisateur."""
        QMessageBox.information(self, title, message)

    def confirm_logout(self) -> bool:
        """Demande confirmation avant de fermer la session."""
        answer = QMessageBox.question(
            self,
            "Terminer la session",
            "Voulez-vous terminer la session maintenant ? Les applications lancees par CESOC seront fermees si possible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return answer == QMessageBox.Yes

    def _build_ui(self) -> None:
        self.user_value = QLabel("-")
        self.email_value = QLabel("-")
        self.workstation_value = QLabel("-")
        self.elapsed_value = QLabel("0 min")
        self.remaining_value = QLabel("0 min")
        self.countdown_value = QLabel("00:00:00")
        self.countdown_value.setStyleSheet("font-size: 28px; font-weight: 700; color: #0f5c4d;")
        self.workspace_value = QLabel("-")
        self.workspace_value.setWordWrap(True)
        self.launched_apps_value = QLabel("0")
        self.status_banner = QLabel("")
        self.status_banner.hide()

        session_box = QGroupBox("Session en cours")
        session_layout = QGridLayout()
        session_layout.addWidget(QLabel("Nom"), 0, 0)
        session_layout.addWidget(self.user_value, 0, 1)
        session_layout.addWidget(QLabel("Email"), 1, 0)
        session_layout.addWidget(self.email_value, 1, 1)
        session_layout.addWidget(QLabel("Poste"), 2, 0)
        session_layout.addWidget(self.workstation_value, 2, 1)
        session_layout.addWidget(QLabel("Temps ecoule"), 3, 0)
        session_layout.addWidget(self.elapsed_value, 3, 1)
        session_layout.addWidget(QLabel("Temps restant"), 4, 0)
        session_layout.addWidget(self.remaining_value, 4, 1)
        session_layout.addWidget(QLabel("Compte a rebours"), 5, 0)
        session_layout.addWidget(self.countdown_value, 5, 1)
        session_layout.addWidget(QLabel("Dossier de travail"), 6, 0)
        session_layout.addWidget(self.workspace_value, 6, 1)
        session_layout.addWidget(QLabel("Applications suivies"), 7, 0)
        session_layout.addWidget(self.launched_apps_value, 7, 1)
        session_box.setLayout(session_layout)

        report_box = QGroupBox("Indicateurs du jour")
        report_layout = QGridLayout()
        self.report_connections = QLabel("0")
        self.report_active = QLabel("0")
        self.report_minutes = QLabel("0")
        self.report_prints = QLabel("0")
        report_layout.addWidget(QLabel("Connexions"), 0, 0)
        report_layout.addWidget(self.report_connections, 0, 1)
        report_layout.addWidget(QLabel("Sessions actives"), 1, 0)
        report_layout.addWidget(self.report_active, 1, 1)
        report_layout.addWidget(QLabel("Minutes utilisees"), 2, 0)
        report_layout.addWidget(self.report_minutes, 2, 1)
        report_layout.addWidget(QLabel("Pages imprimees"), 3, 0)
        report_layout.addWidget(self.report_prints, 3, 1)
        report_box.setLayout(report_layout)

        print_box = QGroupBox("Impression")
        print_layout = QHBoxLayout()
        self.pages_spinbox = QSpinBox()
        self.pages_spinbox.setRange(1, 50)
        self.pages_spinbox.setValue(1)
        self.print_button = QPushButton("Imprimer")
        self.print_button.clicked.connect(lambda: self._on_print(self.pages_spinbox.value()))
        print_layout.addWidget(QLabel("Nombre de pages"))
        print_layout.addWidget(self.pages_spinbox)
        print_layout.addStretch(1)
        print_layout.addWidget(self.print_button)
        print_box.setLayout(print_layout)

        launcher_box = QGroupBox("Applications autorisees")
        launcher_layout = QGridLayout()
        browser_button = QPushButton("Internet")
        browser_button.clicked.connect(self._on_open_browser)
        word_button = QPushButton("Word")
        word_button.clicked.connect(self._on_open_word)
        files_button = QPushButton("Fichiers")
        files_button.clicked.connect(self._on_open_workspace)
        pdf_button = QPushButton("PDF")
        pdf_button.clicked.connect(self._select_pdf)
        launcher_layout.addWidget(browser_button, 0, 0)
        launcher_layout.addWidget(word_button, 0, 1)
        launcher_layout.addWidget(files_button, 1, 0)
        launcher_layout.addWidget(pdf_button, 1, 1)
        launcher_box.setLayout(launcher_layout)

        self.sessions_table = QTableWidget(0, 4)
        self.sessions_table.setHorizontalHeaderLabels(
            ["Email", "Utilisateur", "Poste", "Debut"]
        )

        refresh_button = QPushButton("Actualiser")
        refresh_button.clicked.connect(self._on_refresh)

        logout_button = QPushButton("Fermer ma session")
        logout_button.clicked.connect(self._on_logout)

        header_buttons = QHBoxLayout()
        header_buttons.addWidget(refresh_button)
        header_buttons.addStretch(1)
        header_buttons.addWidget(logout_button)

        layout = QVBoxLayout()
        layout.addLayout(header_buttons)
        layout.addWidget(self.status_banner)
        layout.addWidget(session_box)
        layout.addWidget(report_box)
        layout.addWidget(launcher_box)
        layout.addWidget(print_box)
        layout.addWidget(QLabel("Sessions actives"))
        layout.addWidget(self.sessions_table)
        self.setLayout(layout)

    def _select_pdf(self) -> None:
        base_path = self.workspace_value.text().strip()
        selected_path = self.ask_pdf_path(base_path if base_path and base_path != "-" else "")
        if selected_path:
            self._on_open_pdf(selected_path)
