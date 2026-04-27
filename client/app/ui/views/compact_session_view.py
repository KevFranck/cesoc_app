"""Vue compacte de session pour usage sur bureau Windows normal."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CompactSessionView(QWidget):
    """Panneau flottant recentre sur les besoins utiles pendant la session."""

    LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "cesoc_logo.svg"

    def __init__(
        self,
        on_refresh: Callable[[], None],
        on_hide: Callable[[], None],
        on_change_password: Callable[[], None],
        on_logout: Callable[[], None],
        on_open_browser: Callable[[], None],
        on_open_word: Callable[[], None],
        on_open_workspace: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_refresh = on_refresh
        self._on_hide = on_hide
        self._on_change_password = on_change_password
        self._on_logout = on_logout
        self._on_open_browser = on_open_browser
        self._on_open_word = on_open_word
        self._on_open_workspace = on_open_workspace
        self._build_ui()

    def set_session_header(self, user_name: str, email: str, workstation_name: str) -> None:
        self.user_value.setText(user_name)
        self.identity_value.setText(f"{email} - {workstation_name}")
        self.workstation_value.setText(workstation_name)

    def set_timer(self, elapsed_minutes: int, remaining_minutes: int, formatted_remaining: str) -> None:
        self.elapsed_value.setText(f"{elapsed_minutes} min ecoulees")
        self.remaining_value.setText(f"{remaining_minutes} min restantes")
        self.countdown_value.setText(formatted_remaining)

    def set_workspace_path(self, workspace_path: str) -> None:
        self.workspace_value.setText(workspace_path)

    def set_print_quota(self, pages_used_today: int, remaining_quota: int, daily_quota: int) -> None:
        safe_quota = max(daily_quota, 0)
        safe_used = max(pages_used_today, 0)
        safe_remaining = max(remaining_quota, 0)
        self.quota_value.setText(f"{safe_remaining} page(s) restante(s)")
        self.quota_detail_value.setText(f"{safe_used} / {safe_quota} page(s) utilisee(s) aujourd'hui")
        self.quota_progress.setMaximum(max(safe_quota, 1))
        self.quota_progress.setValue(min(safe_used, max(safe_quota, 1)))
        if safe_quota > 0 and safe_remaining == 0:
            self.quota_state_value.setText("Quota atteint")
            self.quota_state_value.setStyleSheet("color: #ffffff; background: #d92051; border-radius: 10px; padding: 4px 10px; font-weight: 900;")
            self.quota_progress.setStyleSheet(self._progress_style("#d92051"))
        elif safe_quota > 0 and safe_remaining <= 2:
            self.quota_state_value.setText("Bientot atteint")
            self.quota_state_value.setStyleSheet("color: #1a1a2e; background: #f7b700; border-radius: 10px; padding: 4px 10px; font-weight: 900;")
            self.quota_progress.setStyleSheet(self._progress_style("#f7b700"))
        else:
            self.quota_state_value.setText("Disponible")
            self.quota_state_value.setStyleSheet("color: #ffffff; background: #2dad75; border-radius: 10px; padding: 4px 10px; font-weight: 900;")
            self.quota_progress.setStyleSheet(self._progress_style("#2dad75"))

    def set_status_message(self, message: str, level: str = "neutral") -> None:
        colors = {
            "neutral": ("#1e2a38", "#f0f0f0"),
            "warning": ("#f7b700", "#1a1a2e"),
            "danger": ("#d92051", "#ffffff"),
            "success": ("#2dad75", "#ffffff"),
        }
        background, foreground = colors.get(level, colors["neutral"])
        self.status_banner.setText(message)
        self.status_banner.setStyleSheet(
            f"background: {background}; color: {foreground}; border-radius: 8px; "
            "padding: 10px 12px; font-weight: 800;"
        )
        self.status_banner.show()

    def clear_status_message(self) -> None:
        self.status_banner.hide()

    def show_info(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def confirm_logout(self) -> bool:
        answer = QMessageBox.question(
            self,
            "Terminer la session",
            "Voulez-vous terminer la session maintenant ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return answer == QMessageBox.Yes

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #0f1923;
                color: #f0f0f0;
            }
            QFrame#CompactShell {
                background: #1a1a2e;
                border: 1px solid #2dad75;
                border-radius: 18px;
            }
            QFrame#TopCard {
                background: #1e2a38;
                border: 1px solid rgba(54, 189, 231, 0.28);
                border-radius: 16px;
            }
            QFrame#LogoCard {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(54, 189, 231, 0.35);
                border-radius: 16px;
            }
            QFrame#Card {
                background: #1e2a38;
                border: 1px solid rgba(45, 173, 117, 0.28);
                border-radius: 16px;
            }
            QLabel#PanelTitle {
                color: #36bde7;
                font-size: 22px;
                font-weight: 900;
            }
            QLabel#PanelSubtitle {
                color: #f0f0f0;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#UserName {
                color: #ffffff;
                font-size: 18px;
                font-weight: 900;
            }
            QLabel#Identity {
                color: #36bde7;
                font-size: 12px;
                font-weight: 800;
            }
            QLabel#SectionTitle {
                color: #36bde7;
                font-size: 14px;
                font-weight: 900;
            }
            QLabel#SubtleText {
                color: #f0f0f0;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#Countdown {
                color: #ffffff;
                font-size: 34px;
                font-weight: 900;
            }
            QLabel#StatValue {
                color: #ffffff;
                font-size: 18px;
                font-weight: 900;
            }
            QLabel#FieldLabel {
                color: #36bde7;
                font-size: 12px;
                font-weight: 800;
            }
            QLabel#FieldValue {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton {
                min-height: 38px;
                padding: 8px 12px;
                border: none;
                border-radius: 6px;
                background: #2dad75;
                color: #ffffff;
                font-weight: 800;
            }
            QPushButton#GhostButton {
                background: transparent;
                color: #2dad75;
                border: 1px solid #2dad75;
            }
            QPushButton#DangerButton {
                background: #d92051;
                color: #ffffff;
            }
            """
        )

        shell = QFrame()
        shell.setObjectName("CompactShell")

        self.status_banner = QLabel("")
        self.status_banner.hide()
        self.status_banner.setWordWrap(True)

        top_card = QFrame()
        top_card.setObjectName("TopCard")

        logo_card = QFrame()
        logo_card.setObjectName("LogoCard")
        logo_widget = QSvgWidget(str(self.LOGO_PATH))
        logo_widget.setFixedSize(144, 40)
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(12, 10, 12, 10)
        logo_layout.addWidget(logo_widget)
        logo_layout.addStretch(1)
        logo_card.setLayout(logo_layout)

        title = QLabel("Session CESOC")
        title.setObjectName("PanelTitle")
        subtitle = QLabel("Votre session reste suivie pendant que vous utilisez le poste.")
        subtitle.setObjectName("PanelSubtitle")
        subtitle.setWordWrap(True)

        refresh_button = QPushButton("Actualiser")
        refresh_button.setObjectName("GhostButton")
        refresh_button.clicked.connect(self._on_refresh)
        hide_button = QPushButton("Masquer")
        hide_button.setObjectName("GhostButton")
        hide_button.clicked.connect(self._on_hide)
        password_button = QPushButton("Mot de passe")
        password_button.setObjectName("GhostButton")
        password_button.clicked.connect(self._on_change_password)
        logout_button = QPushButton("Terminer")
        logout_button.setObjectName("DangerButton")
        logout_button.clicked.connect(self._on_logout)

        header_actions = QHBoxLayout()
        header_actions.setSpacing(8)
        header_actions.addWidget(refresh_button)
        header_actions.addWidget(hide_button)
        header_actions.addWidget(password_button)
        header_actions.addStretch(1)
        header_actions.addWidget(logout_button)

        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(16, 14, 16, 14)
        top_layout.setSpacing(10)
        top_layout.addWidget(logo_card)
        top_layout.addWidget(title)
        top_layout.addWidget(subtitle)
        top_layout.addLayout(header_actions)
        top_card.setLayout(top_layout)

        self.user_value = QLabel("-")
        self.user_value.setObjectName("UserName")
        self.identity_value = QLabel("-")
        self.identity_value.setObjectName("Identity")
        self.countdown_value = QLabel("00:00:00")
        self.countdown_value.setObjectName("Countdown")
        self.elapsed_value = QLabel("0 min ecoulees")
        self.elapsed_value.setObjectName("SubtleText")
        self.remaining_value = QLabel("0 min restantes")
        self.remaining_value.setObjectName("StatValue")
        self.quota_value = QLabel("0 page(s) restante(s)")
        self.quota_value.setObjectName("StatValue")
        self.quota_state_value = QLabel("Disponible")
        self.quota_state_value.setObjectName("SubtleText")
        self.quota_detail_value = QLabel("0 / 0 utilisees aujourd'hui")
        self.quota_detail_value.setObjectName("SubtleText")
        self.workspace_value = QLabel("-")
        self.workspace_value.setObjectName("FieldValue")
        self.workspace_value.setWordWrap(True)
        self.workstation_value = QLabel("-")
        self.workstation_value.setObjectName("FieldValue")

        self.quota_progress = QProgressBar()
        self.quota_progress.setTextVisible(False)
        self.quota_progress.setMaximum(1)
        self.quota_progress.setValue(0)
        self.quota_progress.setStyleSheet(self._progress_style("#2dad75"))

        identity_card = self._build_card()
        identity_layout = QVBoxLayout()
        identity_layout.setContentsMargins(16, 14, 16, 14)
        identity_layout.setSpacing(3)
        identity_layout.addWidget(self.user_value)
        identity_layout.addWidget(self.identity_value)
        identity_card.setLayout(identity_layout)

        countdown_card = self._build_card()
        countdown_layout = QVBoxLayout()
        countdown_layout.setContentsMargins(16, 14, 16, 14)
        countdown_layout.setSpacing(4)
        countdown_title = QLabel("Temps restant")
        countdown_title.setObjectName("SectionTitle")
        countdown_layout.addWidget(countdown_title)
        countdown_layout.addWidget(self.countdown_value)
        countdown_layout.addWidget(self.remaining_value)
        countdown_layout.addWidget(self.elapsed_value)
        countdown_card.setLayout(countdown_layout)

        quota_card = self._build_card()
        quota_layout = QVBoxLayout()
        quota_layout.setContentsMargins(16, 14, 16, 14)
        quota_layout.setSpacing(6)
        quota_title = QLabel("Quota d'impression")
        quota_title.setObjectName("SectionTitle")
        quota_layout.addWidget(quota_title)
        quota_layout.addWidget(self.quota_value)
        quota_layout.addWidget(self.quota_progress)
        quota_layout.addWidget(self.quota_state_value)
        quota_layout.addWidget(self.quota_detail_value)
        quota_card.setLayout(quota_layout)

        info_card = self._build_card()
        info_layout = QGridLayout()
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setHorizontalSpacing(12)
        info_layout.setVerticalSpacing(8)
        info_title = QLabel("Informations")
        info_title.setObjectName("SectionTitle")
        info_layout.addWidget(info_title, 0, 0, 1, 2)
        info_layout.addWidget(self._field_label("Poste"), 1, 0)
        info_layout.addWidget(self.workstation_value, 1, 1)
        info_layout.addWidget(self._field_label("Dossier de travail"), 2, 0)
        info_layout.addWidget(self.workspace_value, 2, 1)
        info_card.setLayout(info_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(top_card)
        layout.addWidget(self.status_banner)
        layout.addWidget(identity_card)
        layout.addWidget(countdown_card)
        layout.addWidget(quota_card)
        layout.addWidget(info_card)
        shell.setLayout(layout)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(shell)
        self.setLayout(root_layout)

    def _build_card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FieldLabel")
        return label

    def _progress_style(self, chunk_color: str) -> str:
        return (
            "QProgressBar {"
            "min-height: 10px;"
            "max-height: 10px;"
            "background: #0f1923;"
            "border: 1px solid #2f455c;"
            "border-radius: 5px;"
            "}"
            f"QProgressBar::chunk {{ background: {chunk_color}; border-radius: 5px; }}"
        )
