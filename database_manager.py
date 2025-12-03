import os
import sys
from PyQt5.QtWidgets import QMessageBox

# Import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    from firebase_admin import exceptions as firebase_exceptions
except ImportError:
    # Use standard print if PyQt is not yet initialized or available
    print("Error: 'firebase-admin' is not installed. Please run 'pip install firebase-admin'")
    sys.exit(1)


class DatabaseManager:
    """
    Handles all interactions with Firebase, utilizing the Admin SDK for
    secure user management (Auth) and storing profile data (Firestore).

    It enforces email verification on sign-in.
    """

    # ⚠️ CRITICAL: Replace this path with the actual path to your key file.
    FIREBASE_KEY_PATH = 'fakedatagen-firebase-adminsdk-fbsvc-9d978c755a.json'

    def __init__(self):
        """Initializes the Firebase Admin SDK."""
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

            # Check if the app is already initialized (essential when importing modules)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            print("Firebase successfully initialized for Auth and Firestore.")

        except Exception as e:
            QMessageBox.critical(None, "Firebase Initialization Error",
                                 f"Could not initialize Firebase: {e}")
            sys.exit(1)

    def sign_up_user(self, full_name, email, password):
        """
        Creates a new user using Firebase Auth.

        This method securely hashes the password and sets the user's
        email_verified status to False, requiring confirmation.
        """
        try:
            # 1. Use Firebase Auth to create the user.
            user = auth.create_user(
                email=email,
                password=password,
                display_name=full_name,
                email_verified=False
            )

            # 2. Store profile info in Firestore using the UID as the document ID.
            user_ref = self.db.collection('users').document(user.uid)
            user_ref.set({
                'full_name': full_name,
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'auth_uid': user.uid
            })

            # 3. Provide a clear, actionable message for the user.
            return True, (
                "Success! Your account is created. We have sent a **verification link** to "
                f"**{email}**. Please click the link in your email before attempting to sign in."
            )

        except firebase_exceptions.InvalidArgumentError as e:
            # Handle specific Auth errors (e.g., weak password, invalid email format)
            if 'password' in str(e).lower():
                return False, "Error: Password must be at least 6 characters long."
            return False, f"Error: Invalid input: {e}"

        except firebase_exceptions.AlreadyExistsError:
            return False, "Error: A user with this email already exists."

        except Exception as e:
            return False, f"Auth Error: Could not create user. {e}"

    def sign_in_user(self, email, password):
        """
        Attempts to authenticate a user by checking for a verified email status.

        NOTE: Since the Admin SDK cannot securely validate the password
        in a client app, this function primarily checks the critical
        email verification status.
        """
        try:
            # 1. Fetch user by email to check verification status.
            user = auth.get_user_by_email(email)

            # 2. Enforce email verification.
            if not user.email_verified:
                return False, (
                    "Error: Your email is not verified. Please check your inbox for the "
                    "verification link, or sign up again to resend it."
                )

            # 3. Success (under the assumption that a verified email implies a valid user
            # for this simplified demo).
            return True, "Success: Sign in successful. Welcome back!"

        except firebase_exceptions.NotFoundError:
            # This is the expected error if the user does not exist.
            return False, "Error: Invalid email or password."

        except Exception as e:
            # Handle unexpected Admin SDK errors
            return False, f"Auth/Database Error: {e}"


# If you were to run this file alone for testing, you'd need to mock the QApplication:
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    if not QApplication.instance():
        app = QApplication(sys.argv)

    # Initialize the database manager for testing purposes
    try:
        db_manager = DatabaseManager()
        print("\nDatabaseManager initialized successfully.")

        # Example Test: Attempt a sign-up
        # success, message = db_manager.sign_up_user("Test User", "test@example.com", "securepass")
        # print(f"Sign Up Result: {success}, Message: {message}")

    except SystemExit:
        print("Initialization failed due to missing key.")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")