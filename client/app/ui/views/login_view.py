"""Vue de connexion et d'inscription."""

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
    """Ecran d'entree client."""

    LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "cesoc_logo.svg"

    def __init__(
        self,
        on_login: Callable[[str, str, str], None],
        on_register: Callable[[str, str, str, str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_login = on_login
        self._on_register = on_register
        self._mode = "login"
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._update_clock)
        self._build_ui()
        self._apply_mode()
        self._update_clock()
        self._clock_timer.start()

    def set_workstations(self, workstations: list[str], default_name: str | None = None) -> None:
        """Charge la liste des postes disponibles."""
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
            "neutral": ("#1e2a38", "#f0f0f0"),
            "warning": ("#f7b700", "#1a1a2e"),
            "danger": ("#d92051", "#ffffff"),
            "success": ("#2dad75", "#ffffff"),
        }
        background, foreground = palette.get(level, palette["neutral"])
        self.feedback_label.setText(message)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet(
            f"background: {background}; color: {foreground}; border-radius: 10px; "
            "padding: 12px 14px; font-weight: 700; border: 1px solid rgba(255, 255, 255, 0.14);"
        )
        self.feedback_label.show()

    def clear_feedback(self) -> None:
        """Masque le message inline."""
        self.feedback_label.hide()

    def set_busy(self, is_busy: bool) -> None:
        """Bloque temporairement le formulaire."""
        fields = [
            self.email_input,
            self.password_input,
            self.first_name_input,
            self.last_name_input,
            self.workstation_combo,
            self.primary_button,
            self.toggle_button,
        ]
        for field in fields:
            field.setDisabled(is_busy)
        self.primary_button.setText(self._busy_label() if is_busy else self._primary_label())

    def focus_identifier(self) -> None:
        """Redonne le focus au champ principal."""
        self.email_input.setFocus()
        self.email_input.selectAll()

    def show_login_mode(self) -> None:
        """Affiche le mode connexion."""
        self._mode = "login"
        self._apply_mode()

    def show_register_mode(self) -> None:
        """Affiche le mode inscription."""
        self._mode = "register"
        self._apply_mode()

    def reset_form(self) -> None:
        """Nettoie le formulaire."""
        self.email_input.clear()
        self.password_input.clear()
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.clear_feedback()
        self.focus_identifier()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #0f1923;
                color: #f0f0f0;
            }
            QFrame#HeroPanel, QFrame#FormPanel {
                background: #1e2a38;
                border: 1px solid #2dad75;
                border-radius: 18px;
            }
            QFrame#HeroLogoCard {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(54, 189, 231, 0.35);
                border-radius: 16px;
            }
            QFrame#HeroIntro {
                background: rgba(15, 25, 35, 0.88);
                border: 1px solid rgba(45, 173, 117, 0.45);
                border-radius: 16px;
            }
            QFrame#MetricCard, QFrame#InfoPanel {
                background: rgba(255, 255, 255, 0.04);
                border-radius: 14px;
            }
            QFrame#MetricCard {
                border: 1px solid rgba(54, 189, 231, 0.24);
            }
            QFrame#InfoPanel {
                border: 1px solid rgba(247, 183, 0, 0.35);
            }
            QLabel#HeroTitle {
                color: #ffffff;
                font-size: 30px;
                font-weight: 900;
            }
            QLabel#HeroCopy {
                color: #f0f0f0;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#MetricLabel {
                color: #36bde7;
                font-size: 11px;
                font-weight: 800;
            }
            QLabel#MetricValue {
                color: #ffffff;
                font-size: 20px;
                font-weight: 900;
            }
            QLabel#SectionTitle {
                color: #36bde7;
                font-size: 24px;
                font-weight: 900;
            }
            QLabel#SectionCopy {
                color: #f0f0f0;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#TipTitle {
                color: #f7b700;
                font-size: 14px;
                font-weight: 900;
            }
            QLabel#FormLabel {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 800;
            }
            QLineEdit, QComboBox {
                min-height: 44px;
                padding: 6px 10px;
                border: 1px solid #2f455c;
                border-radius: 8px;
                background: #1e2a38;
                color: #ffffff;
                selection-background-color: #36bde7;
                selection-color: #1a1a2e;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #36bde7;
            }
            QComboBox::drop-down {
                border: none;
                width: 26px;
            }
            QPushButton#PrimaryButton {
                min-height: 46px;
                padding: 8px 18px;
                border: none;
                border-radius: 6px;
                background: #2dad75;
                color: #ffffff;
                font-weight: 800;
            }
            QPushButton#PrimaryButton:disabled {
                background: rgba(45, 173, 117, 0.5);
                color: rgba(255, 255, 255, 0.7);
            }
            QPushButton#ToggleButton {
                min-height: 42px;
                padding: 8px 18px;
                border: 1px solid #2dad75;
                border-radius: 6px;
                background: transparent;
                color: #2dad75;
                font-weight: 800;
            }
            QPushButton#ToggleButton:disabled {
                color: rgba(45, 173, 117, 0.5);
                border-color: rgba(45, 173, 117, 0.5);
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
        hero_logo_layout = QHBoxLayout(hero_logo_card)
        hero_logo_layout.setContentsMargins(18, 14, 18, 14)
        hero_logo_layout.addWidget(logo_widget)
        hero_logo_layout.addStretch(1)

        hero_intro = QFrame()
        hero_intro.setObjectName("HeroIntro")
        hero_title = QLabel("Bienvenue au poste d'accueil")
        hero_title.setObjectName("HeroTitle")
        hero_copy = QLabel(
            "Creez votre compte si c'est votre premiere visite, puis connectez-vous pour demarrer votre session en toute autonomie."
        )
        hero_copy.setWordWrap(True)
        hero_copy.setObjectName("HeroCopy")
        hero_intro_layout = QVBoxLayout(hero_intro)
        hero_intro_layout.setContentsMargins(18, 18, 18, 18)
        hero_intro_layout.setSpacing(8)
        hero_intro_layout.addWidget(hero_title)
        hero_intro_layout.addWidget(hero_copy)

        hero_stats = QHBoxLayout()
        hero_stats.setSpacing(10)
        workstation_metric, self.workstation_count_value = self._build_metric_block("Postes disponibles", "0")
        station_metric, self.station_hint_value = self._build_metric_block("Poste selectionne", "-")
        clock_metric, self.clock_value = self._build_metric_block("Heure locale", "-")
        hero_stats.addWidget(workstation_metric)
        hero_stats.addWidget(station_metric)
        hero_stats.addWidget(clock_metric)

        hero_list = QVBoxLayout()
        hero_list.setSpacing(6)
        hero_list.addWidget(self._build_bullet("1. Creez votre compte client si besoin."))
        hero_list.addWidget(self._build_bullet("2. Connectez-vous avec votre mot de passe."))
        hero_list.addWidget(self._build_bullet("3. Pensez a enregistrer vos documents avant la fin de session."))

        hero_layout = QVBoxLayout(hero_panel)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(12)
        hero_layout.addWidget(hero_logo_card)
        hero_layout.addWidget(hero_intro)
        hero_layout.addLayout(hero_stats)
        hero_layout.addLayout(hero_list)
        hero_layout.addStretch(1)

        form_panel = QFrame()
        form_panel.setObjectName("FormPanel")

        self.title_label = QLabel()
        self.title_label.setObjectName("SectionTitle")
        self.subtitle_label = QLabel()
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setObjectName("SectionCopy")

        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Ex: Amina")
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Ex: Diallo")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ex: client@exemple.com")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.returnPressed.connect(self._submit)
        self.workstation_combo = QComboBox()

        self.register_fields = []
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(14)

        self.register_fields.append(self._add_form_row(form_layout, "Prenom", self.first_name_input))
        self.register_fields.append(self._add_form_row(form_layout, "Nom", self.last_name_input))
        form_layout.addRow(self._build_form_label("Adresse email"), self.email_input)
        form_layout.addRow(self._build_form_label("Mot de passe"), self.password_input)
        self.workstation_row = self._add_form_row(form_layout, "Poste", self.workstation_combo)

        self.feedback_label = QLabel("")
        self.feedback_label.hide()

        info_panel = QFrame()
        info_panel.setObjectName("InfoPanel")
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(16, 14, 16, 14)
        tip_title = QLabel("Avant de continuer")
        tip_title.setObjectName("TipTitle")
        info_layout.addWidget(tip_title)
        self.info_text = QLabel()
        self.info_text.setWordWrap(True)
        support_text = QLabel("En cas de difficulte, un membre du personnel peut vous assister.")
        support_text.setWordWrap(True)
        info_layout.addWidget(self.info_text)
        info_layout.addWidget(support_text)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("ToggleButton")
        self.toggle_button.clicked.connect(self._toggle_mode)

        self.primary_button = QPushButton()
        self.primary_button.setObjectName("PrimaryButton")
        self.primary_button.clicked.connect(self._submit)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        actions_layout.addWidget(self.toggle_button)
        actions_layout.addWidget(self.primary_button, 1)

        form_layout_wrapper = QVBoxLayout(form_panel)
        form_layout_wrapper.setContentsMargins(24, 24, 24, 24)
        form_layout_wrapper.setSpacing(12)
        form_layout_wrapper.addWidget(self.title_label)
        form_layout_wrapper.addWidget(self.subtitle_label)
        form_layout_wrapper.addSpacing(12)
        form_layout_wrapper.addLayout(form_layout)
        form_layout_wrapper.addWidget(self.feedback_label)
        form_layout_wrapper.addWidget(info_panel)
        form_layout_wrapper.addStretch(1)
        form_layout_wrapper.addLayout(actions_layout)

        shell_layout = QHBoxLayout(self)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(20)
        shell_layout.addWidget(hero_panel, 6)
        shell_layout.addWidget(form_panel, 5)

    def _build_metric_block(self, label: str, value: str) -> tuple[QFrame, QLabel]:
        frame = QFrame()
        frame.setObjectName("MetricCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        label_widget = QLabel(label)
        label_widget.setObjectName("MetricLabel")
        value_widget = QLabel(value)
        value_widget.setObjectName("MetricValue")
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        return frame, value_widget

    def _build_bullet(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("HeroCopy")
        label.setWordWrap(True)
        label.setStyleSheet("padding: 4px 0; color: #f0f0f0; font-weight: 700;")
        return label

    def _build_form_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FormLabel")
        return label

    def _add_form_row(self, form_layout: QFormLayout, label_text: str, widget: QWidget) -> tuple[QLabel, QWidget]:
        label = self._build_form_label(label_text)
        form_layout.addRow(label, widget)
        return label, widget

    def _set_row_visible(self, row: tuple[QLabel, QWidget], visible: bool) -> None:
        label, widget = row
        label.setVisible(visible)
        widget.setVisible(visible)

    def _apply_mode(self) -> None:
        is_login = self._mode == "login"
        self.title_label.setText("Connexion a votre session" if is_login else "Creer votre compte client")
        self.subtitle_label.setText(
            "Saisissez votre identifiant, votre mot de passe et confirmez le poste sur lequel vous travaillez."
            if is_login
            else "Renseignez vos informations pour creer votre compte, puis utilisez-le ensuite pour vous connecter."
        )
        self.info_text.setText(
            "Vos fichiers doivent etre enregistres dans votre dossier de session ou sur un support externe avant la fin de votre utilisation."
            if is_login
            else "Votre compte vous permettra de revenir plus tard avec le meme identifiant et le meme mot de passe."
        )
        for row in self.register_fields:
            self._set_row_visible(row, not is_login)
        self._set_row_visible(self.workstation_row, is_login)
        self.primary_button.setText(self._primary_label())
        self.toggle_button.setText(
            "Premiere visite ? Creer un compte" if is_login else "J'ai deja un compte"
        )
        self.email_input.setPlaceholderText("Ex: client@exemple.com")
        self.password_input.setPlaceholderText("Mot de passe")

    def _primary_label(self) -> str:
        return "Ouvrir la session" if self._mode == "login" else "Creer mon compte"

    def _busy_label(self) -> str:
        return "Connexion..." if self._mode == "login" else "Inscription..."

    def _toggle_mode(self) -> None:
        self._mode = "register" if self._mode == "login" else "login"
        self.clear_feedback()
        self._apply_mode()
        self.focus_identifier()

    def _update_clock(self) -> None:
        self.clock_value.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"))

    def _submit(self) -> None:
        email = self.email_input.text().strip().lower()
        password = self.password_input.text().strip()

        if not email:
            self.set_feedback("Veuillez saisir votre adresse email avant de continuer.", level="warning")
            self.focus_identifier()
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            self.set_feedback("Veuillez saisir une adresse email valide.", level="warning")
            self.focus_identifier()
            return
        self.clear_feedback()
        if self._mode == "login":
            workstation_name = self.workstation_combo.currentText().strip()
            self._on_login(email, password, workstation_name)
            return

        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        if len(first_name) < 2 or len(last_name) < 2:
            self.set_feedback("Veuillez renseigner votre prenom et votre nom.", level="warning")
            return

        self._on_register(email, first_name, last_name, password)
