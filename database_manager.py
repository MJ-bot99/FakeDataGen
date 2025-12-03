import os
import sys
import requests
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QMessageBox

# Import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    from firebase_admin import exceptions as firebase_exceptions
except ImportError:
    # This check ensures the Admin SDK is present, which is mandatory for this class
    print("Error: 'firebase-admin' is not installed. Please run 'pip install firebase-admin'")
    sys.exit(1)


class DatabaseManager:
    """
    Handles all interactions with Firebase, combining secure user authentication
    via REST API, profile storage via Firestore, and REAL email sending via SMTP.
    """

    # ⚠️ CRITICAL: Replace with your Firebase service account key
    #FIREBASE_KEY_PATH = 'fakedatagen-firebase-adminsdk-fbsvc-d90cad701d.json'

    # ⚠️ FIREBASE CLIENT CONFIG (Needed for REST API calls)
    FIREBASE_API_KEY = "AIzaSyDu1qYcw0UmfYI_81UowPscboktELhE3Zc"
    FIREBASE_PROJECT_ID = "fakedatagen"

    # 💥 NEW: Use the specific channel domain for verification links
    VERIFICATION_DOMAIN = "fakedatagen-e31b9.web.app"

    # REST API endpoint for password sign-in
    _SIGN_IN_URL = (
        "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword"
    )

    # ⚠️ EMAIL CONFIGURATION - YOU MUST SET THESE
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'danysrael720@gmail.com',
        # NOTE: This must be a Google App Password, often separated by spaces.
        'sender_password': 'vmsg carj xpqd mtsc',
        'use_tls': True,
        'sender_name': 'DataForge'
    }

    # Simple rate limiting: Store the last time an email was sent to an address
    LAST_EMAIL_SENT = {}
    RESEND_DELAY_SECONDS = 60

    def __init__(self):
        """Initialize Firebase and test email configuration."""
        self._initialize_firebase()
        self.email_enabled = self._check_email_config()

        # Check for REST API Key configuration
        if self.FIREBASE_API_KEY == "AIzaSyYOUR_API_KEY_HERE":
            QMessageBox.warning(None, "Configuration Required",
                                "Please update Firebase API Key and Project ID in 'database_manager.py'.")

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not os.path.exists(self.FIREBASE_KEY_PATH):
            QMessageBox.critical(None, "Configuration Error",
                                 f"Firebase key not found at: {self.FIREBASE_KEY_PATH}")
            sys.exit(1)

        try:
            cred = credentials.Certificate(self.FIREBASE_KEY_PATH)
            if not firebase_admin._apps:
                self.app = firebase_admin.initialize_app(cred)
            else:
                self.app = firebase_admin.get_app()

            self.db = firestore.client()
            print("✅ Firebase initialized successfully")

        except Exception as e:
            QMessageBox.critical(None, "Firebase Error", f"Could not initialize Firebase: {e}")
            sys.exit(1)

    def _check_email_config(self):
        """Check if email is properly configured."""
        if (self.EMAIL_CONFIG['sender_email'] == 'YOUR_EMAIL@gmail.com' or
                self.EMAIL_CONFIG['sender_password'] == 'YOUR_APP_PASSWORD'):
            print("\n" + "=" * 60)
            print("⚠️  EMAIL NOT CONFIGURED - Verification emails won't be sent!")
            print("=" * 60)
            return False
        return True

    def _verify_password_with_rest_api(self, email, password):
        """
        Securely verifies a user's password using the Firebase Auth REST API.
        Returns (True, id_token) on success, (False, error_message) on failure.
        """
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        url = f"{self._SIGN_IN_URL}?key={self.FIREBASE_API_KEY}"

        try:
            response = requests.post(url, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                # Password is correct. Store the ID token (not used here but essential for API calls)
                id_token = response_data.get('idToken')
                return True, id_token
            else:
                # Handle REST API errors
                error_code = response_data.get('error', {}).get('message', 'UNKNOWN_ERROR')
                if error_code == "EMAIL_NOT_FOUND" or error_code == "INVALID_PASSWORD":
                    return False, "❌ Invalid email or password."
                else:
                    print(f"REST API Error: {error_code}")
                    return False, f"❌ Sign-in failed: {error_code}"

        except requests.exceptions.RequestException:
            return False, "❌ A network error occurred. Check your connection."

    def _send_verification_email(self, email, verification_link):
        """
        Actually sends a verification email via SMTP.
        Returns True if email was sent successfully.
        """
        if not self.email_enabled:
            print(f"📧 [DEV MODE] Verification link for {email}: {verification_link}")
            print("⚠️  Email not sent - Update EMAIL_CONFIG to send real emails")
            return False

        # --- Rate Limit Check ---
        current_time = time.time()
        last_sent = self.LAST_EMAIL_SENT.get(email, 0)
        if current_time - last_sent < self.RESEND_DELAY_SECONDS:
            print(f"📧 Rate limit hit for {email}. Skipping email send.")
            return True  # Pretend it was successful to avoid error messages in UI
        # --- End Rate Limit Check ---

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your Email - DataForge'
            msg['From'] = f"{self.EMAIL_CONFIG['sender_name']} <{self.EMAIL_CONFIG['sender_email']}>"
            msg['To'] = email

            # Create HTML email content (unchanged)
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #A68CC8 0%, #8d70b5 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">Verify Your Email</h1>
                </div>

                <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <p>Hello,</p>
                    <p>Thank you for creating an account with <strong>DataForge</strong>!</p>
                    <p>Please verify your email address by clicking the button below:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_link}"
                           style="background: #A68CC8; color: white; padding: 12px 30px;
                                  text-decoration: none; border-radius: 5px; font-weight: bold;
                                  display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; word-break: break-all;">
                        <code style="font-size: 12px;">{verification_link}</code>
                    </div>
                    <p>This verification link will expire in 24 hours.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        If you're having trouble clicking the button, copy and paste the URL above
                        into your web browser.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
                    <p>© {time.strftime('%Y')} DataForge. All rights reserved.</p>
                </div>
            </body>
            </html>
            """
            text = f"""
            Verify Your Email - DataForge
            Please verify your email address by clicking this link:
            {verification_link}
            If you can't click the link, copy and paste it into your browser.
            This link will expire in 24 hours.
            If you didn't create this account, please ignore this email.
            """

            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            # Connect to SMTP server and send email
            print(f"📤 Connecting to SMTP server: {self.EMAIL_CONFIG['smtp_server']}")

            # IMPORTANT: Remove spaces from App Password before logging in
            clean_password = self.EMAIL_CONFIG['sender_password'].replace(" ", "")

            if self.EMAIL_CONFIG['use_tls']:
                server = smtplib.SMTP(self.EMAIL_CONFIG['smtp_server'], self.EMAIL_CONFIG['smtp_port'])
                server.starttls()  # Enable TLS encryption
            else:
                server = smtplib.SMTP_SSL(self.EMAIL_CONFIG['smtp_server'], self.EMAIL_CONFIG['smtp_port'])

            server.login(self.EMAIL_CONFIG['sender_email'], clean_password)
            server.send_message(msg)
            server.quit()

            self.LAST_EMAIL_SENT[email] = current_time  # Update timestamp on success

            print(f"✅ Verification email sent to: {email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print(f"❌ SMTP Authentication failed. Check your email and password.")
            print("   Make sure you're using an App Password, not your regular password.")
            return False
        except Exception as e:
            # This will catch other errors like connection failures
            print(f"❌ Failed to send email: {e}")
            return False

    def _generate_verification_link(self, email):
        """Generate a verification link using Firebase Admin SDK, using the custom channel domain."""
        try:
            # Use the specific channel domain provided by the user
            verification_page_url = 'https://fakedatagen.web.app/verify.html'

            action_code_settings = auth.ActionCodeSettings(
                url=verification_page_url,
                handle_code_in_app=False
            )

            # Generate the verification link
            verification_link = auth.generate_email_verification_link(
                email,
                action_code_settings=action_code_settings
            )

            print(f"✅ Verification link generated successfully")
            print(f"🔗 Verification link generated for: {email}")

            return verification_link

        except firebase_exceptions.FirebaseError as e:
            print(f"❌ Firebase error: {e}")
            if "UNAUTHORIZED_DOMAIN" in str(e):
                print("\n🔧 IMPORTANT: You need to authorize your domain in Firebase Console!")
            return None

        except Exception as e:
            print(f"❌ Failed to generate verification link: {e}")
            return None

    def sign_up_user(self, full_name, email, password):
        """
        Creates a new user and sends a REAL verification email.
        """
        try:
            # 1. Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=full_name,
                email_verified=False
            )

            print(f"✅ User created: {user.uid}")

            # 2. Generate verification link
            verification_link = self._generate_verification_link(email)
            email_sent = False

            if verification_link:
                # 3. Send actual verification email
                email_sent = self._send_verification_email(email, verification_link)

            # 4. Store user data in Firestore
            user_ref = self.db.collection('users').document(user.uid)
            user_ref.set({
                'full_name': full_name,
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'auth_uid': user.uid,
                'email_verified': False
            })

            # 5. Return success message
            if email_sent:
                return True, (
                    "🎉 Account created successfully!\n\n"
                    "📧 A verification email has been sent to:\n"
                    f"   {email}\n\n"
                    "📋 Please check your inbox and spam folder.\n"
                    "You must verify your email before signing in."
                )
            else:
                return True, (
                    "🎉 Account created!\n\n"
                    "⚠️  Verification email failed to send. Please check your SMTP configuration and try resending it from the Sign In screen."
                )

        except firebase_exceptions.InvalidArgumentError as e:
            if 'password' in str(e).lower():
                return False, "❌ Password must be at least 6 characters."
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
        Securely checks password via REST API, then checks for email verification
        status using Firebase Admin SDK.
        """

        # 1. SECURELY Verify Password first via REST API
        password_ok, token_or_message = self._verify_password_with_rest_api(email, password)

        if not password_ok:
            # Token_or_message contains the error message from the REST API
            return False, token_or_message

            # 2. Password is correct. Now check email verification status using Admin SDK.
        try:
            # Use Admin SDK to get the user's current status
            user = auth.get_user_by_email(email)

            # 3. Enforce email verification.
            if not user.email_verified:

                # Resend logic: Try to generate and send a new link
                verification_link = self._generate_verification_link(email)
                email_sent = False

                if verification_link:
                    # _send_verification_email contains the rate limiting logic
                    email_sent = self._send_verification_email(email, verification_link)

                if email_sent:
                    return False, (
                        "❌ Email not verified!\n\n"
                        "📧 A new verification email has been sent to:\n"
                        f"   {email}\n\n"
                        "Please verify your email before signing in."
                    )
                else:
                    return False, (
                        "❌ Email not verified! Please check your inbox or try resending the email."
                    )

            # 4. Success!
            return True, "✅ Sign in successful! Welcome back!"

        except firebase_exceptions.NotFoundError:
            # Should not happen if REST API succeeded, but kept as a fallback.
            return False, "❌ Invalid email or password."

        except Exception as e:
            return False, f"❌ Error checking verification status: {e}"

    def resend_verification_email(self, email):
        """Resends verification email to a user."""
        try:
            user = auth.get_user_by_email(email)

            if user.email_verified:
                return True, "✅ Email is already verified!"

            verification_link = self._generate_verification_link(email)

            if verification_link:
                email_sent = self._send_verification_email(email, verification_link)
                if email_sent:
                    return True, f"📧 Verification email resent to {email}"
                else:
                    return False, "❌ Failed to send email (check console logs for SMTP error)"
            else:
                return False, "❌ Failed to generate verification link"

        except firebase_exceptions.NotFoundError:
            return False, "❌ User not found"
        except Exception as e:
            return False, f"❌ Error: {e}"