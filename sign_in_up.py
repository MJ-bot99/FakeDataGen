import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy, QStackedWidget, QMainWindow
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
# Import DatabaseManager (assuming it's in the same directory)
from database_manager import DatabaseManager

# 💥 IMPORTING THE ACTUAL MAIN INTERFACE FROM main_interface.py
from main_interface import MainInterface


# ====================================================================
# --- Base Auth Form (UI Styles and Container) ---
# ====================================================================
class AuthForm(QWidget):
    switch_form = pyqtSignal(str)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setStyleSheet(self.get_styles())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(8)

        title_label = QLabel("DataForge")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("Secure Authentication Interface")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        header_layout.addSpacing(40)

        main_layout.addLayout(header_layout)

        # Card Frame
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(40, 30, 40, 50)
        self.card_layout.setSpacing(15)
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)

        # Tab buttons container
        tab_frame = QFrame()
        tab_frame.setObjectName("tabFrame")
        tab_layout = QHBoxLayout(tab_frame)
        tab_layout.setSpacing(0)
        tab_layout.setContentsMargins(4, 4, 4, 4)

        self.btn_signin = QPushButton("Sign In")
        self.btn_signin.setObjectName("tabButton")
        self.btn_signin.clicked.connect(lambda: self.switch_form.emit("signin"))

        self.btn_signup = QPushButton("Sign Up")
        self.btn_signup.setObjectName("tabButton")
        self.btn_signup.clicked.connect(lambda: self.switch_form.emit("signup"))

        tab_layout.addWidget(self.btn_signin)
        tab_layout.addWidget(self.btn_signup)
        self.card_layout.addWidget(tab_frame)

    def set_active_tab(self, form_name):
        self.btn_signin.setProperty("active", form_name == "signin")
        self.btn_signup.setProperty("active", form_name == "signup")

        self.btn_signin.style().polish(self.btn_signin)
        self.btn_signup.style().polish(self.btn_signup)

    def get_styles(self):
        FOCUS_PURPLE = "#a07ade"
        PURPLE_HOVER = "#8d70b5"
        ERROR_RED = "#dc2626"
        SUCCESS_GREEN = "#10b981"
        INFO_BLUE = "#3b82f6"

        CARD_MIN_WIDTH = 450
        NEW_BG_COLOR = "#f7f7f7"
        CARD_BG_COLOR = "#ffffff"
        BUTTON_LILAC = "#A68CC8"
        TAB_FRAME_BG = "#ededed"

        return f"""
        /* --- General and Main Window --- */
        QWidget {{
            background-color: {NEW_BG_COLOR};
            font-family: Arial, sans-serif;
        }}

        /* --- Title and Subtitle Styles --- */
        QLabel#titleLabel {{
            color: #333333;
            font-size: 32px;
            font-weight: bold;
            margin: 0;
            padding: 0;
        }}

        QLabel#subtitleLabel {{
            color: #666666;
            font-size: 16px;
            font-weight: normal;
            margin: 0;
            padding: 0;
        }}

        /* --- Card Frame --- */
        #card {{
            background-color: {CARD_BG_COLOR};
            border-radius: 16px;
            min-width: {CARD_MIN_WIDTH}px;
            border: 1px solid #d9d9d9;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
        }}

        QStackedWidget {{
            background-color: transparent;
        }}

        /* --- Tab Frame and Buttons --- */
        #tabFrame {{
            background-color: {TAB_FRAME_BG};
            border-radius: 8px;
            padding: 0.5px;
        }}

        QPushButton#tabButton {{
            padding: 6px 20px;
            border: none;
            font-weight: 500;
            font-size: 13px;
            color: #666666;
            background-color: transparent;
            border-radius: 6px;
            min-height: 20px;
            margin: 0.5px;
        }}

        QPushButton#tabButton[active="true"] {{
            color: #000000;
            background-color: #ffffff;
            font-weight: 600;
            box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.05);
            border-radius: 6px;
        }}

        /* --- Input Fields and Labels --- */
        QLabel {{
            color: #222222;
            font-weight: 500;
            margin-top: 15px;
            margin-bottom: 5px;
            font-size: 13px;
            background: transparent;
        }}

        QLineEdit {{
            padding: 10px 15px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            background-color: #ffffff;
            color: #000000;
        }}

        QLineEdit::placeholder {{
            color: #999999;
            font-weight: 400;
        }}

        QLineEdit[error="true"] {{
            border: 1px solid {ERROR_RED};
            background-color: rgba(220, 38, 38, 0.05);
        }}

        QLineEdit:focus {{
            border: 1px solid {FOCUS_PURPLE};
            outline: 2px solid rgba(160, 122, 222, 0.2);
        }}

        /* --- Main Action Button --- */
        QPushButton#mainButton {{
            background-color: {BUTTON_LILAC};
            color: white;
            padding: 14px 20px;
            border-radius: 10px;
            font-weight: 600;
            margin-top: 25px;
            font-size: 14px;
        }}
        QPushButton#mainButton:hover {{
            background-color: {PURPLE_HOVER};
        }}

        /* --- Secondary Button --- */
        QPushButton#secondaryButton {{
            background-color: #f3f4f6;
            color: #374151;
            border: 1px solid #d1d5db;
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton#secondaryButton:hover {{
            background-color: #e5e7eb;
        }}

        /* --- Message Labels --- */
        QLabel#errorMessage {{
            color: {ERROR_RED};
            font-size: 13px;
            font-weight: 500;
            padding: 8px 12px;
            background-color: rgba(220, 38, 38, 0.08);
            border-radius: 8px;
            margin-top: 5px;
            margin-bottom: 5px;
            border: 1px solid rgba(220, 38, 38, 0.2);
        }}

        QLabel#successMessage {{
            color: {SUCCESS_GREEN};
            font-size: 13px;
            font-weight: 500;
            padding: 8px 12px;
            background-color: rgba(16, 185, 129, 0.08);
            border-radius: 8px;
            margin-top: 5px;
            margin-bottom: 5px;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}

        QLabel#infoMessage {{
            color: {INFO_BLUE};
            font-size: 13px;
            font-weight: 500;
            padding: 8px 12px;
            background-color: rgba(59, 130, 246, 0.08);
            border-radius: 8px;
            margin-top: 5px;
            margin-bottom: 5px;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }}
        """


# ====================================================================
# --- Sign In Form (Signal Added) ---
# ====================================================================
class SignInForm(QWidget):
    # New signal emitted upon successful sign-in
    login_success = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setObjectName("signInForm")
        layout = QVBoxLayout(self)

        # Initialize timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_messages)

        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@example.com")
        layout.addWidget(self.email_input)

        # Password
        layout.addWidget(QLabel("Password"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("********")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Resend verification button
        self.resend_btn = QPushButton("Resend Verification Email")
        self.resend_btn.setObjectName("secondaryButton")
        self.resend_btn.clicked.connect(self.handle_resend_verification)
        self.resend_btn.setVisible(False)
        layout.addWidget(self.resend_btn)

        # Messages
        self.error_message = QLabel("")
        self.error_message.setObjectName("errorMessage")
        self.error_message.setVisible(False)
        self.error_message.setWordWrap(True)
        layout.addWidget(self.error_message)

        self.success_message = QLabel("")
        self.success_message.setObjectName("successMessage")
        self.success_message.setVisible(False)
        self.success_message.setWordWrap(True)
        layout.addWidget(self.success_message)

        self.info_message = QLabel("")
        self.info_message.setObjectName("infoMessage")
        self.info_message.setVisible(False)
        layout.addWidget(self.info_message)

        # Sign In button
        btn = QPushButton("Sign In")
        btn.setObjectName("mainButton")
        # Connect button to handler
        btn.clicked.connect(self.handle_sign_in)
        layout.addWidget(btn)

        layout.addStretch()

    def hide_messages(self):
        """Hides all temporary message labels."""
        self.error_message.setVisible(False)
        self.success_message.setVisible(False)
        self.info_message.setVisible(False)

    def clear_messages(self):
        """Clear all messages and error states."""
        self.timer.stop()
        self.error_message.setText("")
        self.success_message.setText("")
        self.hide_messages()
        self.resend_btn.setVisible(False)

        self.email_input.setProperty("error", False)
        self.email_input.style().polish(self.email_input)
        self.password_input.setProperty("error", False)
        self.password_input.style().polish(self.password_input)

    def show_message(self, message_type, message, focus_field=None, autohide=True):
        """Show a message inline, optionally starting a 5-second autohide timer."""
        self.clear_messages()

        target_label = None

        if message_type == "error":
            target_label = self.error_message
        elif message_type == "success":
            target_label = self.success_message
        elif message_type == "info":
            target_label = self.info_message

        if target_label:
            target_label.setText(message)
            target_label.setVisible(True)

            if autohide:
                self.timer.start(5000)  # 5000 milliseconds = 5 seconds

        if "not verified" in message.lower():
            self.resend_btn.setVisible(True)

        if focus_field == "email":
            self.email_input.setProperty("error", True)
            self.email_input.style().polish(self.email_input)
            self.email_input.setFocus()
        elif focus_field == "password":
            self.password_input.setProperty("error", True)
            self.password_input.style().polish(self.password_input)
            self.password_input.setFocus()

    def handle_resend_verification(self):
        """Handle resend verification email request"""
        email = self.email_input.text().strip()

        if not email:
            self.show_message("error", "Please enter your email to resend verification.", "email")
            return

        self.resend_btn.setText("Sending...")
        self.resend_btn.setEnabled(False)

        # Display a persistent message while sending (autohide=False)
        self.show_message("info", "Resending verification email...", autohide=False)

        success, message = self.db_manager.resend_verification_email(email)

        if success:
            self.show_message("success", message)
        else:
            self.show_message("error", message)

        self.resend_btn.setText("Resend Verification Email")
        self.resend_btn.setEnabled(True)

    def handle_sign_in(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        self.clear_messages()

        if not email or not password:
            self.show_message("error", "Please enter both email and password.",
                              "email" if not email else "password")
            return

        if "@" not in email or "." not in email:
            self.show_message("error", "Please enter a valid email address.", "email")
            return

        # Attempt sign in (Uses the secure REST API check in DatabaseManager)
        success, message = self.db_manager.sign_in_user(email, password)

        # Always clear password after an attempt for security
        self.password_input.clear()

        if success:
            self.show_message("success", message)
            self.email_input.clear()  # Clear email on success

            # 💥 EMIT SIGNAL TO SWITCH TO MAIN INTERFACE
            self.login_success.emit()

        else:
            self.show_message("error", message, "email")


# ====================================================================
# --- Sign Up Form ---
# ====================================================================
class SignUpForm(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setObjectName("signUpForm")
        layout = QVBoxLayout(self)

        # Initialize timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_messages)

        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        # Full Name
        layout.addWidget(QLabel("Full Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("John Doe")
        layout.addWidget(self.name_input)

        # Email
        layout.addWidget(QLabel("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("you@example.com")
        layout.addWidget(self.email_input)

        # Password
        layout.addWidget(QLabel("Password (Min 6 characters)"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("********")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Messages (Error, Success)
        self.error_message = QLabel("")
        self.error_message.setObjectName("errorMessage")
        self.error_message.setVisible(False)
        layout.addWidget(self.error_message)

        self.success_message = QLabel("")
        self.success_message.setObjectName("successMessage")
        self.success_message.setVisible(False)
        layout.addWidget(self.success_message)

        # Info message (This is now used for temporary messages only)
        self.info_message = QLabel("")
        self.info_message.setObjectName("infoMessage")
        self.info_message.setVisible(False)
        layout.addWidget(self.info_message)

        # Create Account button
        btn = QPushButton("Create Account")
        btn.setObjectName("mainButton")
        btn.clicked.connect(self.handle_sign_up)
        layout.addWidget(btn)

        layout.addStretch()

    def hide_messages(self):
        """Hides all temporary message labels."""
        self.error_message.setVisible(False)
        self.success_message.setVisible(False)
        self.info_message.setVisible(False)

    def clear_messages(self):
        """Clear all messages and error states."""
        self.timer.stop()
        self.error_message.setText("")
        self.success_message.setText("")
        self.info_message.setText("")
        self.hide_messages()

        # Clear error states from input fields
        self.name_input.setProperty("error", False)
        self.name_input.style().polish(self.name_input)
        self.email_input.setProperty("error", False)
        self.email_input.style().polish(self.email_input)
        self.password_input.setProperty("error", False)
        self.password_input.style().polish(self.password_input)

    def show_message(self, message_type, message, focus_field=None, autohide=True):
        """Show a message inline, starting a 5-second autohide timer."""
        self.clear_messages()

        target_label = None

        if message_type == "error":
            target_label = self.error_message
        elif message_type == "success":
            target_label = self.success_message
        elif message_type == "info":
            target_label = self.info_message

        if target_label:
            target_label.setText(message)
            target_label.setVisible(True)

            if autohide:
                self.timer.start(5000)  # 5000 milliseconds = 5 seconds

        # Highlight problematic fields
        if focus_field == "name":
            self.name_input.setProperty("error", True)
            self.name_input.style().polish(self.name_input)
            self.name_input.setFocus()
        elif focus_field == "email":
            self.email_input.setProperty("error", True)
            self.email_input.style().polish(self.email_input)
            self.email_input.setFocus()
        elif focus_field == "password":
            self.password_input.setProperty("error", True)
            self.password_input.style().polish(self.password_input)
            self.password_input.setFocus()

    def handle_sign_up(self):
        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        self.clear_messages()

        # Validation
        if not full_name or not email or not password:
            self.show_message("error", "All fields must be filled out.",
                              "name" if not full_name else "email" if not email else "password")
            return

        if "@" not in email or "." not in email:
            self.show_message("error", "Please enter a valid email address.", "email")
            return

        if len(password) < 6:
            self.show_message("error", "Password must be at least 6 characters long.", "password")
            return

        # Show info message while processing (autohide=False)
        self.show_message("info", "Creating account and sending verification email...", autohide=False)

        # Attempt sign up
        success, message = self.db_manager.sign_up_user(full_name, email, password)

        # Now show the result, which will auto-hide
        if success:
            self.show_message("success", message)
            # Clear input fields on success
            self.name_input.clear()
            self.email_input.clear()
            self.password_input.clear()
        else:
            focus_field = "email"
            if "name" in message.lower():
                focus_field = "name"
            elif "password" in message.lower():
                focus_field = "password"

            self.show_message("error", message, focus_field)


# ====================================================================
# --- Auth Window (Manages Stacks) ---
# ====================================================================
class AuthWindow(AuthForm):
    """
    The authentication widget structure that manages the stacked sign-in/sign-up forms.
    """
    STATIC_OVERHEAD = 220

    # Propagate the login signal from SignInForm
    login_success = pyqtSignal()

    def __init__(self, db_manager, initial_form="signup"):
        super().__init__(db_manager)

        self.stacked = QStackedWidget()

        self.signup_widget = SignUpForm(self.db_manager)
        self.signin_widget = SignInForm(self.db_manager)

        # Connect the SignInForm signal to AuthWindow's signal
        self.signin_widget.login_success.connect(self.login_success.emit)

        self.stacked.addWidget(self.signup_widget)
        self.stacked.addWidget(self.signin_widget)

        self.card_layout.addWidget(self.stacked)

        self.switch_form.connect(self.change_form)
        self.change_form(initial_form)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_card_height)
        self.timer.start(50)

    def update_card_height(self):
        """Dynamically adjusts the card height based on the current form's content."""
        current_widget = self.stacked.currentWidget()
        content_height = current_widget.sizeHint().height()

        new_card_height = content_height + self.STATIC_OVERHEAD

        if abs(self.card.height() - new_card_height) > 5:
            self.card.setFixedHeight(new_card_height)
            self.card.parentWidget().updateGeometry()

    def change_form(self, form_name):
        """Switches the view and updates the card size."""
        self.signup_widget.clear_messages()
        self.signin_widget.clear_messages()

        if form_name == "signin":
            self.stacked.setCurrentWidget(self.signin_widget)
        else:
            self.stacked.setCurrentWidget(self.signup_widget)

        self.set_active_tab(form_name)
        self.update_card_height()


# ====================================================================
# --- Main Application Container (Handles Switching) ---
# ====================================================================
class AuthAppContainer(QMainWindow):

    def __init__(self, db_manager, initial_form="signup"):
        super().__init__()
        self.setWindowTitle("DataForge Authentication Interface")
        self.setGeometry(100, 100, 1440, 1024)

        # 1. Create the main stacked widget for the entire application
        self.app_stack = QStackedWidget()
        self.setCentralWidget(self.app_stack)

        # 2. Instantiate the Auth UI (which manages sign-in/sign-up forms)
        self.auth_component = AuthWindow(db_manager, initial_form)

        # 3. Instantiate the Main Interface
        self.main_component = MainInterface()

        # 4. Add components to the main stack
        self.app_stack.addWidget(self.auth_component)  # Index 0: Auth
        self.app_stack.addWidget(self.main_component)  # Index 1: Main App

        # 5. Connect the signal from the AuthWindow to the switch method
        self.auth_component.login_success.connect(self.show_main_interface)

        # Start on the Auth screen
        self.app_stack.setCurrentIndex(0)

    def show_main_interface(self):
        """Switches the QStackedWidget view to the main application interface."""
        # Switch to the MainInterface (Index 1)
        self.app_stack.setCurrentIndex(1)
        self.setWindowTitle("DataForge - Main Application")


# Renamed to AuthAppContainer to resolve the import conflict
MainWindow = AuthAppContainer