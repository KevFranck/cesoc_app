"""Vue compacte de session pour usage sur bureau Windows normal."""

from collections.abc import Callable

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

    def __init__(
        self,
        on_refresh: Callable[[], None],
        on_hide: Callable[[], None],
        on_logout: Callable[[], None],
        on_open_browser: Callable[[], None],
        on_open_word: Callable[[], None],
        on_open_workspace: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_refresh = on_refresh
        self._on_hide = on_hide
        self._on_logout = on_logout
        self._on_open_browser = on_open_browser
        self._on_open_word = on_open_word
        self._on_open_workspace = on_open_workspace
        self._build_ui()

    def set_session_header(self, user_name: str, external_id: str, workstation_name: str) -> None:
        self.user_value.setText(user_name)
        self.identity_value.setText(f"{external_id} - {workstation_name}")
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
        self.quota_detail_value.setText(f"{safe_used} / {safe_quota} utilisees aujourd'hui")
        self.quota_progress.setMaximum(max(safe_quota, 1))
        self.quota_progress.setValue(min(safe_used, max(safe_quota, 1)))
        if safe_quota > 0 and safe_remaining == 0:
            self.quota_state_value.setText("Quota atteint")
            self.quota_state_value.setStyleSheet("color: #8a2138; font-weight: 800;")
            self.quota_progress.setStyleSheet(self._progress_style("#c94b61"))
        elif safe_quota > 0 and safe_remaining <= 2:
            self.quota_state_value.setText("Bientot atteint")
            self.quota_state_value.setStyleSheet("color: #8b5a00; font-weight: 800;")
            self.quota_progress.setStyleSheet(self._progress_style("#d49a2a"))
        else:
            self.quota_state_value.setText("Disponible")
            self.quota_state_value.setStyleSheet("color: #1c6441; font-weight: 800;")
            self.quota_progress.setStyleSheet(self._progress_style("#2dad75"))

    def set_status_message(self, message: str, level: str = "neutral") -> None:
        colors = {
            "neutral": ("#eef3f0", "#28413b"),
            "warning": ("#fff3d9", "#8b5a00"),
            "danger": ("#fde4e1", "#8a2138"),
            "success": ("#e4f5ea", "#1c6441"),
        }
        background, foreground = colors.get(level, colors["neutral"])
        self.status_banner.setText(message)
        self.status_banner.setStyleSheet(
            f"background: {background}; color: {foreground}; border: 1px solid transparent; "
            "border-radius: 12px; padding: 10px 12px; font-weight: 700;"
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
                background: #eef6f2;
                color: #17322d;
            }
            QFrame#CompactShell {
                background: #fffdf8;
                border: 1px solid #d7e0d9;
                border-radius: 22px;
            }
            QFrame#HeaderStrip {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f4f4f, stop:0.52 #2dad75, stop:0.78 #36bde7, stop:1 #f7b700);
                border-radius: 18px;
            }
            QFrame#Card {
                background: #f7faf7;
                border: 1px solid #d9e0d9;
                border-radius: 16px;
            }
            QLabel#PanelTitle {
                color: #ffffff;
                font-size: 20px;
                font-weight: 900;
            }
            QLabel#PanelSubtitle {
                color: #ffffff;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#UserName {
                color: #173d35;
                font-size: 17px;
                font-weight: 800;
            }
            QLabel#Identity {
                color: #4b625c;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#SectionTitle {
                color: #183a34;
                font-size: 14px;
                font-weight: 900;
            }
            QLabel#SubtleText {
                color: #5f746f;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#Countdown {
                color: #173d35;
                font-size: 32px;
                font-weight: 900;
            }
            QLabel#StatValue {
                color: #173d35;
                font-size: 17px;
                font-weight: 800;
            }
            QLabel#FieldLabel {
                color: #5f746f;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel#FieldValue {
                color: #173d35;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton {
                min-height: 38px;
                padding: 8px 12px;
                border: none;
                border-radius: 12px;
                background: #2dad75;
                color: #ffffff;
                font-weight: 800;
            }
            QPushButton#GhostButton {
                background: #f3f7f4;
                color: #173d35;
                border: 1px solid #c8d3cc;
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

        header_strip = QFrame()
        header_strip.setObjectName("HeaderStrip")
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
        logout_button = QPushButton("Terminer")
        logout_button.setObjectName("DangerButton")
        logout_button.clicked.connect(self._on_logout)

        header_actions = QHBoxLayout()
        header_actions.setSpacing(8)
        header_actions.addWidget(refresh_button)
        header_actions.addWidget(hide_button)
        header_actions.addStretch(1)
        header_actions.addWidget(logout_button)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(5)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addLayout(header_actions)
        header_strip.setLayout(header_layout)

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
        identity_layout.setContentsMargins(16, 12, 16, 12)
        identity_layout.setSpacing(2)
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
        quota_layout.setSpacing(5)
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
        info_layout.setVerticalSpacing(6)
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
        layout.addWidget(header_strip)
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
            "background: #e5ebe7;"
            "border: none;"
            "border-radius: 5px;"
            "}"
            f"QProgressBar::chunk {{ background: {chunk_color}; border-radius: 5px; }}"
        )
