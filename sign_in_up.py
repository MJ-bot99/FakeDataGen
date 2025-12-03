import os
import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy, QMessageBox, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

# Import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    from firebase_admin import exceptions as firebase_exceptions
except ImportError:
    print("Error: 'firebase-admin' is not installed. Please run 'pip install firebase-admin'")
    sys.exit(1)


# ====================================================================
# --- 1. Database Manager (Handles Firebase Auth and Firestore) ---
# ====================================================================

class DatabaseManager:
    """
    Handles all interactions with Firebase, utilizing the Admin SDK for
    secure user management (Auth) and storing profile data (Firestore).
    """

    # ⚠️ CRITICAL: Replace this path with the actual path to your key file.
    FIREBASE_KEY_PATH = 'fakedatagen-firebase-adminsdk-fbsvc-9d978c755a.json'

    # ⚠️ You need to set these values from your Firebase Console
    # Go to: Project Settings > General > Your Apps > Web App > Config
    FIREBASE_API_KEY = "AIzaSyYOUR_API_KEY_HERE"
    FIREBASE_PROJECT_ID = "your-project-id"

    def __init__(self):
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initializes the Firebase Admin SDK for both Auth and Firestore."""

        # Check if the configuration file exists
        if not os.path.exists(self.FIREBASE_KEY_PATH):
            QMessageBox.critical(None, "Configuration Error",
                                 f"Service account key not found at: {self.FIREBASE_KEY_PATH}\n"
                                 "Please download your Firebase private key and place it in the project directory.")
            sys.exit(1)

        try:
            cred = credentials.Certificate(self.FIREBASE_KEY_PATH)

            # Check if the app is already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            print("Firebase successfully initialized for Auth and Firestore.")

        except Exception as e:
            QMessageBox.critical(None, "Firebase Initialization Error",
                                 f"Could not initialize Firebase: {e}")
            sys.exit(1)

    def _send_verification_email(self, email):
        """
        Sends email verification using Firebase Admin SDK.
        Returns True if verification email was sent successfully.
        """
        try:
            # Generate email verification link
            action_code_settings = auth.ActionCodeSettings(
                url=f'https://{self.FIREBASE_PROJECT_ID}.firebaseapp.com/__/auth/action',
                handle_code_in_app=False
            )

            # Generate the verification link
            verification_link = auth.generate_email_verification_link(
                email,
                action_code_settings=action_code_settings
            )

            # In a real application, you would send this link via email
            # For now, we'll print it to console and simulate sending

            print("=" * 60)
            print(f"📧 VERIFICATION EMAIL FOR: {email}")
            print("=" * 60)
            print(f"Verification Link: {verification_link}")
            print("=" * 60)
            print("\n⚠️  In a production environment:")
            print("1. This link would be sent via email using a service like SendGrid")
            print("2. You would use: send_email(email, 'Verify Email', verification_link)")
            print("3. Or trigger a Firebase Cloud Function to send the email")
            print("=" * 60)

            # For demo purposes, we'll return True to simulate email sent
            # In production, you should actually send the email here
            return True

        except Exception as e:
            print(f"Error generating verification link: {e}")
            return False

    def sign_up_user(self, full_name, email, password):
        """
        Creates a new user using Firebase Auth, sends verification email,
        and stores profile data in Firestore.
        """
        try:
            # 1. Use Firebase Auth to create the user.
            user = auth.create_user(
                email=email,
                password=password,
                display_name=full_name,
                email_verified=False  # Email will be verified when user clicks link
            )

            print(f"✅ User created with UID: {user.uid}")

            # 2. Send verification email
            print("📤 Attempting to send verification email...")
            email_sent = self._send_verification_email(email)

            if not email_sent:
                print("⚠️  Could not send verification email, but user was created")
                # Continue anyway - user can request verification email later

            # 3. Store profile info in Firestore using the UID.
            user_ref = self.db.collection('users').document(user.uid)
            user_ref.set({
                'full_name': full_name,
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'auth_uid': user.uid,
                'email_verified': False,
                'verification_sent': email_sent
            })

            print(f"✅ User profile saved to Firestore: {user.uid}")

            # 4. Return success message
            if email_sent:
                return True, (
                    "🎉 Account created successfully!\n\n"
                    "📧 A verification email has been sent to:\n"
                    f"   {email}\n\n"
                    "Please check your inbox (and spam folder) for the verification link.\n"
                    "You must verify your email before you can sign in."
                )
            else:
                return True, (
                    "🎉 Account created!\n\n"
                    "⚠️  Verification email could not be sent.\n"
                    "Please contact support or use 'Forgot Password' to verify your email."
                )

        except firebase_exceptions.InvalidArgumentError as e:
            if 'password' in str(e).lower():
                return False, "❌ Password must be at least 6 characters long."
            return False, f"❌ Invalid input: {e}"

        except firebase_exceptions.AlreadyExistsError:
            return False, "❌ A user with this email already exists."

        except Exception as e:
            error_msg = str(e)
            if "INVALID_EMAIL" in error_msg:
                return False, "❌ Please enter a valid email address."
            elif "WEAK_PASSWORD" in error_msg:
                return False, "❌ Password is too weak. Use at least 6 characters."
            else:
                return False, f"❌ Could not create account: {e}"

    def sign_in_user(self, email, password):
        """
        Checks for email verification status using Firebase Auth.

        Note: Firebase Admin SDK cannot verify passwords directly.
        In a real application, you should use Firebase Client SDK for password verification.
        This is a simplified version that checks email verification status.
        """
        try:
            # 1. Fetch user by email to check verification status.
            user = auth.get_user_by_email(email)

            print(f"🔍 Found user: {user.uid}, Email verified: {user.email_verified}")

            # 2. Enforce email verification.
            if not user.email_verified:
                # Offer to resend verification email
                email_sent = self._send_verification_email(email)

                if email_sent:
                    return False, (
                        "❌ Email not verified!\n\n"
                        "📧 A new verification email has been sent to:\n"
                        f"   {email}\n\n"
                        "Please verify your email before signing in."
                    )
                else:
                    return False, (
                        "❌ Email not verified!\n\n"
                        "Please check your inbox for the verification link.\n"
                        "You can also click 'Sign Up' again to resend the verification email."
                    )

            # 3. In a real app, you would verify password here using Firebase Client SDK
            # For this demo, we'll assume password is correct if email is verified
            print(f"✅ User {email} is verified and can sign in")
            return True, "✅ Sign in successful! Welcome back!"

        except firebase_exceptions.NotFoundError:
            return False, "❌ Invalid email or password."

        except Exception as e:
            return False, f"❌ Error: {e}"

    def resend_verification_email(self, email):
        """
        Resends verification email to a user.
        """
        try:
            # Check if user exists
            user = auth.get_user_by_email(email)

            if user.email_verified:
                return True, "✅ Email is already verified!"

            # Send verification email
            email_sent = self._send_verification_email(email)

            if email_sent:
                return True, f"📧 Verification email resent to {email}"
            else:
                return False, "❌ Failed to resend verification email"

        except firebase_exceptions.NotFoundError:
            return False, "❌ User not found"
        except Exception as e:
            return False, f"❌ Error: {e}"


# ====================================================================
# --- 2. Base Auth Form (UI Styles and Container) ---
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

        subtitle_label = QLabel("Generate realistic fake data for testing")
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
        # --- Color Definitions ---
        FOCUS_PURPLE = "#a07ade"
        PURPLE_HOVER = "#8d70b5"
        ERROR_RED = "#dc2626"
        SUCCESS_GREEN = "#10b981"
        INFO_BLUE = "#3b82f6"
        WARNING_YELLOW = "#f59e0b"

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

        /* General tab button styles */
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

        /* Active Tab Button */
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

        /* Error state for input fields */
        QLineEdit[error="true"] {{
            border: 1px solid {ERROR_RED};
            background-color: rgba(220, 38, 38, 0.05);
        }}

        /* Focus state with subtle outline */
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

        QLabel#warningMessage {{
            color: {WARNING_YELLOW};
            font-size: 13px;
            font-weight: 500;
            padding: 8px 12px;
            background-color: rgba(245, 158, 11, 0.08);
            border-radius: 8px;
            margin-top: 5px;
            margin-bottom: 5px;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}
        """


# ====================================================================
# --- 3. Sign In Form ---
# ====================================================================
class SignInForm(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setObjectName("signInForm")
        layout = QVBoxLayout(self)

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
        self.info_message.setWordWrap(True)
        layout.addWidget(self.info_message)

        # Sign In button
        btn = QPushButton("Sign In")
        btn.setObjectName("mainButton")
        btn.clicked.connect(self.handle_sign_in)
        layout.addWidget(btn)

        layout.addStretch()

    def clear_messages(self):
        """Clear all messages"""
        self.error_message.setText("")
        self.error_message.setVisible(False)
        self.success_message.setText("")
        self.success_message.setVisible(False)
        self.info_message.setText("")
        self.info_message.setVisible(False)
        self.resend_btn.setVisible(False)

        # Clear error states from input fields
        self.email_input.setProperty("error", False)
        self.email_input.style().polish(self.email_input)
        self.password_input.setProperty("error", False)
        self.password_input.style().polish(self.password_input)

    def show_message(self, message_type, message, focus_field=None):
        """Show a message inline"""
        self.clear_messages()

        if message_type == "error":
            self.error_message.setText(message)
            self.error_message.setVisible(True)
        elif message_type == "success":
            self.success_message.setText(message)
            self.success_message.setVisible(True)
        elif message_type == "info":
            self.info_message.setText(message)
            self.info_message.setVisible(True)

        # Show resend button if email not verified error
        if "not verified" in message.lower():
            self.resend_btn.setVisible(True)

        # Highlight problematic fields
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
            self.show_message("error", "Please enter your email.", "email")
            return

        self.resend_btn.setText("Sending...")
        self.resend_btn.setEnabled(False)

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

        # Clear previous messages
        self.clear_messages()

        # Validation
        if not email and not password:
            self.show_message("error", "Please enter both email and password.", "email")
            return
        if not email:
            self.show_message("error", "Please enter your email.", "email")
            return
        if not password:
            self.show_message("error", "Please enter your password.", "password")
            return

        # Check for valid email format
        if "@" not in email or "." not in email:
            self.show_message("error", "Please enter a valid email address.", "email")
            return

        # Attempt sign in
        success, message = self.db_manager.sign_in_user(email, password)

        if success:
            self.show_message("success", message)
            # Clear password field
            self.password_input.clear()
            # TODO: Transition to main application window here
        else:
            self.show_message("error", message, "email")


# ====================================================================
# --- 4. Sign Up Form ---
# ====================================================================
class SignUpForm(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setObjectName("signUpForm")
        layout = QVBoxLayout(self)

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

        # Email verification info
        self.info_message = QLabel("")
        self.info_message.setObjectName("infoMessage")
        self.info_message.setVisible(False)
        self.info_message.setWordWrap(True)
        layout.addWidget(self.info_message)

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

        # Create Account button
        btn = QPushButton("Create Account")
        btn.setObjectName("mainButton")
        btn.clicked.connect(self.handle_sign_up)
        layout.addWidget(btn)

        layout.addStretch()

    def clear_messages(self):
        """Clear all messages"""
        self.error_message.setText("")
        self.error_message.setVisible(False)
        self.success_message.setText("")
        self.success_message.setVisible(False)
        self.info_message.setText("")
        self.info_message.setVisible(False)

        # Clear error states from input fields
        self.name_input.setProperty("error", False)
        self.name_input.style().polish(self.name_input)
        self.email_input.setProperty("error", False)
        self.email_input.style().polish(self.email_input)
        self.password_input.setProperty("error", False)
        self.password_input.style().polish(self.password_input)

    def show_message(self, message_type, message, focus_field=None):
        """Show a message inline"""
        self.clear_messages()

        if message_type == "error":
            self.error_message.setText(message)
            self.error_message.setVisible(True)
        elif message_type == "success":
            self.success_message.setText(message)
            self.success_message.setVisible(True)
        elif message_type == "info":
            self.info_message.setText(message)
            self.info_message.setVisible(True)

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

        # Clear previous messages
        self.clear_messages()

        # Show info message about email verification
        self.show_message("info", "After creating your account, you'll receive a verification email.")

        # Validation
        if not full_name or not email or not password:
            self.show_message("error", "All fields must be filled out.",
                              "name" if not full_name else "email" if not email else "password")
            return

        # Check for valid email format
        if "@" not in email or "." not in email:
            self.show_message("error", "Please enter a valid email address.", "email")
            return

        # Check password length
        if len(password) < 6:
            self.show_message("error", "Password must be at least 6 characters long.", "password")
            return

        # Attempt sign up
        success, message = self.db_manager.sign_up_user(full_name, email, password)

        if success:
            self.show_message("success", message)
            # Clear all fields
            self.name_input.clear()
            self.email_input.clear()
            self.password_input.clear()
        else:
            # Determine which field to focus based on error message
            focus_field = "email"
            if "name" in message.lower():
                focus_field = "name"
            elif "password" in message.lower():
                focus_field = "password"

            self.show_message("error", message, focus_field)


# ====================================================================
# --- 5. Main Application Window ---
# ====================================================================
class MainWindow(AuthForm):
    """
    The main window structure that manages the stacked sign-in/sign-up forms.
    """
    STATIC_OVERHEAD = 220  # Increased to accommodate messages

    def __init__(self, db_manager, initial_form="signup"):
        super().__init__(db_manager)
        self.setWindowTitle("DataForge Authentication")

        self.resize(1440, 1024)

        # 1. Setup the stacked widget
        self.stacked = QStackedWidget()

        # 2. Instantiate forms
        self.signup_widget = SignUpForm(self.db_manager)
        self.signin_widget = SignInForm(self.db_manager)
        self.stacked.addWidget(self.signup_widget)
        self.stacked.addWidget(self.signin_widget)

        # 3. Add the stacked widget to the card layout
        self.card_layout.addWidget(self.stacked)

        # 4. Connect signals and set initial view
        self.switch_form.connect(self.change_form)
        self.change_form(initial_form)

        # 5. Timer to dynamically update card height
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_card_height)
        self.timer.start(50)

    def update_card_height(self):
        """Dynamically adjusts the card height based on the current form's content."""
        current_widget = self.stacked.currentWidget()
        content_height = current_widget.minimumSizeHint().height()

        new_card_height = content_height + self.STATIC_OVERHEAD

        if abs(self.card.height() - new_card_height) > 5:
            self.card.setFixedHeight(new_card_height)

    def change_form(self, form_name):
        """Switches the view and updates the card size."""
        # Clear any existing messages when switching forms
        self.signup_widget.clear_messages()
        self.signin_widget.clear_messages()

        if form_name == "signin":
            self.stacked.setCurrentWidget(self.signin_widget)
        else:
            self.stacked.setCurrentWidget(self.signup_widget)

        self.set_active_tab(form_name)
        # Force an update immediately after switching
        self.update_card_height()


# ====================================================================
# --- 6. Application Entry Point ---
# ====================================================================
def main():
    app = QApplication(sys.argv)

    # Initialize database manager
    print("Initializing Firebase Database Manager...")
    db_manager = DatabaseManager()

    # Check if Firebase is properly configured
    if db_manager.FIREBASE_API_KEY == "AIzaSyYOUR_API_KEY_HERE":
        print("\n⚠️  WARNING: You need to configure Firebase API Key!")
        print("Please update these values in DatabaseManager class:")
        print(f"1. FIREBASE_API_KEY = 'YOUR_FIREBASE_WEB_API_KEY'")
        print(f"2. FIREBASE_PROJECT_ID = 'your-project-id'")
        print("\nGet these from Firebase Console:")
        print("Project Settings > General > Your Apps > Web App > Config")

        # Show warning but continue for demo
        QMessageBox.warning(None, "Configuration Required",
                            "Please update Firebase API Key and Project ID in the code.\n"
                            "Check the console for instructions.")

    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()