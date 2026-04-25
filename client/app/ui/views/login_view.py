"""Vue de connexion."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QDateTime, Qt, QTimer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class LoginView(QWidget):
    """Ecran de connexion utilisateur."""

    LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "cesoc_logo.svg"

    def __init__(self, on_login: Callable[[str, str], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_login = on_login
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_clock)
        self._build_ui()
        self._update_clock()
        self._clock_timer.start()

    def set_workstations(self, workstations: list[str], default_name: str | None = None) -> None:
        """Charge la liste des postes."""
        self.workstation_combo.clear()
        self.workstation_combo.addItems(workstations)
        self.workstation_count_value.setText(str(len(workstations)))

        if default_name:
            index = self.workstation_combo.findText(default_name, Qt.MatchExactly)
            if index >= 0:
                self.workstation_combo.setCurrentIndex(index)
                self.station_hint_value.setText(default_name)

        if workstations and not default_name:
            self.station_hint_value.setText(workstations[0])

    def set_feedback(self, message: str, level: str = "neutral") -> None:
        """Affiche un message inline sous le formulaire."""
        palette = {
            "neutral": ("#eef3f0", "#37534c"),
            "warning": ("#fff3d9", "#8b5a00"),
            "danger": ("#fde4e1", "#8a2138"),
            "success": ("#e4f5ea", "#1c6441"),
        }
        background, foreground = palette.get(level, palette["neutral"])
        self.feedback_label.setText(message)
        self.feedback_label.setStyleSheet(
            f"background: {background}; color: {foreground}; border-radius: 12px; padding: 10px 12px; font-weight: 600;"
        )
        self.feedback_label.show()

    def clear_feedback(self) -> None:
        """Masque le message inline."""
        self.feedback_label.hide()

    def set_busy(self, is_busy: bool) -> None:
        """Bloque temporairement le formulaire pendant l'authentification."""
        self.external_id_input.setDisabled(is_busy)
        self.workstation_combo.setDisabled(is_busy)
        self.login_button.setDisabled(is_busy)
        self.login_button.setText("Connexion..." if is_busy else "Ouvrir la session")

    def focus_identifier(self) -> None:
        """Redonne le focus au champ principal."""
        self.external_id_input.setFocus()
        self.external_id_input.selectAll()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #eef6f2;
                color: #17322d;
            }
            QFrame#HeroPanel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #0f4f4f, stop: 0.45 #2dad75, stop: 0.72 #36bde7, stop: 1 #f7b700);
                border-radius: 24px;
            }
            QFrame#HeroIntro {
                background: rgba(10, 33, 36, 0.34);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 18px;
            }
            QFrame#HeroLogoCard {
                background: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 20px;
            }
            QFrame#FormPanel {
                background: #fffdf8;
                border: 1px solid #e1e3db;
                border-radius: 24px;
            }
            QLabel#HeroTitle {
                color: #ffffff;
                font-size: 33px;
                font-weight: 900;
            }
            QLabel#HeroCopy {
                color: #f8fffc;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#MetricLabel {
                color: #3f5650;
                font-size: 11px;
                font-weight: 800;
            }
            QLabel#MetricValue {
                color: #173d35;
                font-size: 22px;
                font-weight: 800;
            }
            QLabel#SectionTitle {
                color: #173d35;
                font-size: 26px;
                font-weight: 800;
            }
            QLabel#SectionCopy {
                color: #405550;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#TipTitle {
                color: #173d35;
                font-size: 14px;
                font-weight: 800;
            }
            QLabel#FormLabel {
                color: #304742;
                font-size: 13px;
                font-weight: 700;
            }
            QLineEdit, QComboBox {
                min-height: 42px;
                padding: 6px 10px;
                border: 1px solid #d7ddd5;
                border-radius: 12px;
                background: white;
                color: #17322d;
            }
            QPushButton {
                min-height: 46px;
                padding: 8px 18px;
                border: none;
                border-radius: 999px;
                background: #d92051;
                color: white;
                font-weight: 800;
            }
            QPushButton:disabled {
                background: #97b2ac;
                color: #edf3f1;
            }
            """
        )

        hero_panel = QFrame()
        hero_panel.setObjectName("HeroPanel")
        hero_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hero_logo_card = QFrame()
        hero_logo_card.setObjectName("HeroLogoCard")
        logo_widget = QSvgWidget(str(self.LOGO_PATH))
        logo_widget.setFixedSize(190, 52)
        hero_logo_layout = QHBoxLayout()
        hero_logo_layout.setContentsMargins(18, 14, 18, 14)
        hero_logo_layout.addWidget(logo_widget)
        hero_logo_layout.addStretch(1)
        hero_logo_card.setLayout(hero_logo_layout)

        hero_intro = QFrame()
        hero_intro.setObjectName("HeroIntro")

        hero_title = QLabel("Bienvenue au poste d'accueil")
        hero_title.setObjectName("HeroTitle")
        hero_copy = QLabel(
            "Connectez-vous pour demarrer votre session, consulter Internet, ouvrir vos documents et suivre votre temps d'utilisation."
        )
        hero_copy.setWordWrap(True)
        hero_copy.setObjectName("HeroCopy")

        hero_intro_layout = QVBoxLayout()
        hero_intro_layout.setContentsMargins(18, 18, 18, 18)
        hero_intro_layout.setSpacing(8)
        hero_intro_layout.addWidget(hero_title)
        hero_intro_layout.addWidget(hero_copy)
        hero_intro.setLayout(hero_intro_layout)

        hero_stats = QHBoxLayout()
        workstation_metric, self.workstation_count_value = self._build_metric_block(
            "Postes disponibles", "0"
        )
        station_metric, self.station_hint_value = self._build_metric_block(
            "Poste selectionne", "-"
        )
        clock_metric, self.clock_value = self._build_metric_block("Heure locale", "-")
        hero_stats.addWidget(workstation_metric)
        hero_stats.addWidget(station_metric)
        hero_stats.addWidget(clock_metric)

        hero_list = QVBoxLayout()
        hero_list.addWidget(self._build_bullet("1. Identifiez-vous avec votre code client."))
        hero_list.addWidget(self._build_bullet("2. Verifiez le poste choisi avant de continuer."))
        hero_list.addWidget(self._build_bullet("3. Pensez a enregistrer vos documents avant la fin de session."))

        hero_layout = QVBoxLayout()
        hero_layout.setContentsMargins(28, 28, 28, 28)
        hero_layout.setSpacing(10)
        hero_layout.addWidget(hero_logo_card)
        hero_layout.addSpacing(6)
        hero_layout.addWidget(hero_intro)
        hero_layout.addSpacing(12)
        hero_layout.addLayout(hero_stats)
        hero_layout.addSpacing(18)
        hero_layout.addLayout(hero_list)
        hero_layout.addStretch(1)
        hero_panel.setLayout(hero_layout)

        form_panel = QFrame()
        form_panel.setObjectName("FormPanel")

        title = QLabel("Connexion a votre session")
        title.setObjectName("SectionTitle")

        subtitle = QLabel(
            "Saisissez votre identifiant et confirmez le poste sur lequel vous travaillez."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("SectionCopy")

        self.external_id_input = QLineEdit()
        self.external_id_input.setPlaceholderText("Ex: CLI-001")
        self.external_id_input.returnPressed.connect(self._submit)

        self.workstation_combo = QComboBox()

        form_layout = QFormLayout()
        identifier_label = QLabel("Identifiant client")
        identifier_label.setObjectName("FormLabel")
        workstation_label = QLabel("Poste")
        workstation_label.setObjectName("FormLabel")
        form_layout.addRow(identifier_label, self.external_id_input)
        form_layout.addRow(workstation_label, self.workstation_combo)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(14)

        self.login_button = QPushButton("Ouvrir la session")
        self.login_button.clicked.connect(self._submit)

        self.feedback_label = QLabel("")
        self.feedback_label.hide()

        info_panel = QFrame()
        info_panel.setStyleSheet(
            "QFrame { background: #f6f6f1; border: 1px solid #d7ddd5; border-radius: 16px; }"
        )
        info_layout = QVBoxLayout()
        tip_title = QLabel("Avant de continuer")
        tip_title.setObjectName("TipTitle")
        info_layout.addWidget(tip_title)
        info_text = QLabel(
            "Vos fichiers doivent etre enregistres dans votre dossier de session ou sur un support externe avant la fin de votre utilisation."
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        support_text = QLabel("En cas de difficulte, un membre du personnel peut vous assister.")
        support_text.setWordWrap(True)
        info_layout.addWidget(support_text)
        info_panel.setLayout(info_layout)

        form_layout_wrapper = QVBoxLayout()
        form_layout_wrapper.setContentsMargins(28, 28, 28, 28)
        form_layout_wrapper.setSpacing(10)
        form_layout_wrapper.addWidget(title)
        form_layout_wrapper.addWidget(subtitle)
        form_layout_wrapper.addSpacing(18)
        form_layout_wrapper.addLayout(form_layout)
        form_layout_wrapper.addSpacing(8)
        form_layout_wrapper.addWidget(self.feedback_label)
        form_layout_wrapper.addWidget(info_panel)
        form_layout_wrapper.addSpacing(12)
        form_layout_wrapper.addWidget(self.login_button)
        form_layout_wrapper.addStretch(1)
        form_panel.setLayout(form_layout_wrapper)

        shell_layout = QHBoxLayout()
        shell_layout.addWidget(hero_panel, 6)
        shell_layout.addWidget(form_panel, 5)
        shell_layout.setSpacing(20)
        self.setLayout(shell_layout)

    def _build_metric_block(self, label: str, value: str) -> tuple[QFrame, QLabel]:
        frame = QFrame()
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        frame.setStyleSheet(
            "QFrame { background: #f8fbf9; border: 1px solid rgba(23, 61, 53, 0.18); border-radius: 18px; }"
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)
        label_widget = QLabel(label)
        label_widget.setObjectName("MetricLabel")
        value_widget = QLabel(value)
        value_widget.setObjectName("MetricValue")
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        frame.setLayout(layout)
        return frame, value_widget

    def _build_bullet(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("HeroCopy")
        label.setWordWrap(True)
        label.setStyleSheet("padding: 6px 0; color: #f5fffb; font-weight: 700;")
        return label

    def _update_clock(self) -> None:
        current_time = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        if hasattr(self, "clock_value"):
            self.clock_value.setText(current_time)

    def _submit(self) -> None:
        external_id = self.external_id_input.text().strip()
        workstation_name = self.workstation_combo.currentText().strip()

        if not external_id:
            self.set_feedback("Veuillez saisir un identifiant client avant de continuer.", level="warning")
            self.focus_identifier()
            return

        self.clear_feedback()
        self._on_login(external_id, workstation_name)
