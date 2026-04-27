"""Vue mini de session, visible mais tres discrete."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class MiniSessionView(QWidget):
    """Bandeau de session leger, lisible et discret."""

    LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "cesoc_logo.svg"

    def __init__(
        self,
        on_expand: Callable[[], None],
        on_logout: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_expand = on_expand
        self._on_logout = on_logout
        self._build_ui()

    def set_session_header(self, user_name: str, workstation_name: str) -> None:
        self.identity_value.setText(f"{user_name} - {workstation_name}")

    def set_timer(self, formatted_remaining: str) -> None:
        self.countdown_value.setText(formatted_remaining)

    def set_print_quota(self, remaining_quota: int, daily_quota: int) -> None:
        if daily_quota <= 0:
            self.quota_value.setText("Impression indisponible")
            return
        self.quota_value.setText(f"{remaining_quota}/{daily_quota} pages")

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #0f1923;
                color: #f0f0f0;
            }
            QFrame#MiniShell {
                background: #1e2a38;
                border: 1px solid #2dad75;
                border-radius: 14px;
            }
            QLabel#MiniIdentity {
                color: #f0f0f0;
                font-size: 11px;
                font-weight: 800;
            }
            QLabel#MiniQuota {
                color: #36bde7;
                font-size: 11px;
                font-weight: 800;
            }
            QLabel#MiniCountdown {
                color: #ffffff;
                font-size: 20px;
                font-weight: 900;
            }
            QPushButton {
                min-height: 28px;
                padding: 4px 10px;
                border: none;
                border-radius: 6px;
                background: #d92051;
                color: #ffffff;
                font-weight: 800;
            }
            QPushButton#GhostButton {
                background: transparent;
                color: #2dad75;
                border: 1px solid #2dad75;
            }
            """
        )

        shell = QFrame()
        shell.setObjectName("MiniShell")

        logo_widget = QSvgWidget(str(self.LOGO_PATH))
        logo_widget.setFixedSize(94, 28)
        self.identity_value = QLabel("-")
        self.identity_value.setObjectName("MiniIdentity")
        self.quota_value = QLabel("Impression indisponible")
        self.quota_value.setObjectName("MiniQuota")
        self.countdown_value = QLabel("00:00:00")
        self.countdown_value.setObjectName("MiniCountdown")

        expand_button = QPushButton("Ouvrir")
        expand_button.setObjectName("GhostButton")
        expand_button.clicked.connect(self._on_expand)
        logout_button = QPushButton("Terminer")
        logout_button.clicked.connect(self._on_logout)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        info_layout.addWidget(logo_widget)
        info_layout.addWidget(self.identity_value)
        info_layout.addWidget(self.quota_value)

        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)
        actions_layout.addWidget(expand_button)
        actions_layout.addWidget(logout_button)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        layout.addLayout(info_layout, 1)
        layout.addWidget(self.countdown_value)
        layout.addLayout(actions_layout)
        shell.setLayout(layout)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(shell)
        self.setLayout(root_layout)
