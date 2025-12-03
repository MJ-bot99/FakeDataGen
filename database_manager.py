import os
import sys
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
    print("Error: 'firebase-admin' is not installed. Please run 'pip install firebase-admin'")
    sys.exit(1)


class DatabaseManager:
    """
    Handles all interactions with Firebase with REAL email sending.
    """

    # ⚠️ Replace with your Firebase service account key
    #FIREBASE_KEY_PATH = 'fakedatagen-firebase-adminsdk-fbsvc-d90cad701d.json'

    # ⚠️ EMAIL CONFIGURATION - YOU MUST SET THESE
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',  # For Gmail
        'smtp_port': 587,  # 587 for TLS, 465 for SSL
        'sender_email': 'danysrael720@gmail.com',  # Your Gmail address
        'sender_password': 'nsag ecay gpse cdsy',  # App password from Google
        'use_tls': True,  # Use TLS encryption
        'sender_name': 'DataForge'
    }

    def __init__(self):
        """Initialize Firebase and test email configuration."""
        self._initialize_firebase()
        self.email_enabled = self._check_email_config()

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
            print("To enable email sending, update EMAIL_CONFIG with:")
            print("1. Your Gmail address")
            print("2. An App Password (not your regular password)")
            print("\nGet App Password from:")
            print("https://myaccount.google.com/apppasswords")
            print("=" * 60 + "\n")
            return False
        return True

    def _send_verification_email(self, email, verification_link):
        """
        Actually sends a verification email via SMTP.
        Returns True if email was sent successfully.
        """
        if not self.email_enabled:
            print(f"📧 [DEV MODE] Verification link for {email}: {verification_link}")
            print("⚠️  Email not sent - Update EMAIL_CONFIG to send real emails")
            return False

        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verify Your Email - DataForge'
            msg['From'] = f"{self.EMAIL_CONFIG['sender_name']} <{self.EMAIL_CONFIG['sender_email']}>"
            msg['To'] = email

            # Create HTML email content
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

            # Plain text version (for email clients that don't support HTML)
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

            if self.EMAIL_CONFIG['use_tls']:
                server = smtplib.SMTP(self.EMAIL_CONFIG['smtp_server'], self.EMAIL_CONFIG['smtp_port'])
                server.starttls()  # Enable TLS encryption
            else:
                server = smtplib.SMTP_SSL(self.EMAIL_CONFIG['smtp_server'], self.EMAIL_CONFIG['smtp_port'])

            server.login(self.EMAIL_CONFIG['sender_email'], self.EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            server.quit()

            print(f"✅ Verification email sent to: {email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print(f"❌ SMTP Authentication failed. Check your email and password.")
            print("   Make sure you're using an App Password, not your regular password.")
            return False
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def _generate_verification_link(self, email):
        """Generate a verification link using Firebase Admin SDK."""
        try:
            # Get project ID
            project_id = self.app.project_id if hasattr(self, 'app') else 'fakedatagen'

            # ✅ YOUR FIREBASE HOSTING URL
            verification_page_url = f'https://{project_id}.web.app/verify.html'
            # OR: f'https://{project_id}.firebaseapp.com/verify.html'

            print(f"🔗 Using Firebase Hosting URL: {verification_page_url}")

            # Create action code settings
            action_code_settings = auth.ActionCodeSettings(
                url=verification_page_url,  # ✅ Points to YOUR Firebase Hosting page
                handle_code_in_app=False
            )

            print(f"🔗 Generating verification link for: {email}")
            print(f"🔗 Redirect URL: {action_code_settings.url}")

            # Generate the verification link
            verification_link = auth.generate_email_verification_link(
                email,
                action_code_settings=action_code_settings
            )

            print(f"✅ Verification link generated successfully")

            # Also log the link for testing
            print(f"🔗 Full verification link: {verification_link[:100]}...")

            return verification_link

        except firebase_exceptions.FirebaseError as e:
            print(f"❌ Firebase error: {e}")

            if "UNAUTHORIZED_DOMAIN" in str(e):
                print("\n🔧 IMPORTANT: You need to authorize your domain in Firebase Console!")
                print("1. Go to: https://console.firebase.google.com/")
                print("2. Select your project: fakedatagen")
                print("3. Go to: Authentication → Sign-in method")
                print("4. Scroll to 'Authorized domains'")
                print("5. Click 'Add domain' and add:")
                print(f"   - {project_id}.web.app")
                print(f"   - {project_id}.firebaseapp.com")
                print("6. Save and wait 5 minutes")
                print("\n⚠️  Until then, emails will show links in console only.")

            # Fallback: Show link in console for testing
            print(f"\n📧 DEV MODE: Manual verification for {email}")
            print("Use Firebase Console to verify email:")
            print("1. Go to: https://console.firebase.google.com/")
            print("2. Select your project")
            print("3. Go to: Authentication → Users")
            print(f"4. Find: {email}")
            print("5. Click ••• → 'Enable user'")

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

            if not verification_link:
                # Store user anyway even if link generation fails
                print("⚠️  Could not generate verification link, but user was created")
            else:
                # 3. Send actual verification email
                email_sent = self._send_verification_email(email, verification_link)

                if not email_sent and self.email_enabled:
                    print("⚠️  Email sending failed, but user was created")

            # 4. Store user data in Firestore
            user_ref = self.db.collection('users').document(user.uid)
            user_ref.set({
                'full_name': full_name,
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'auth_uid': user.uid,
                'email_verified': False
            })

            # 5. Return appropriate message based on email status
            if self.email_enabled:
                if verification_link:
                    return True, (
                        "🎉 Account created successfully!\n\n"
                        "📧 A verification email has been sent to:\n"
                        f"   {email}\n\n"
                        "📋 Please check your inbox and spam folder.\n"
                        "You must verify your email before signing in."
                    )
                else:
                    return True, (
                        "⚠️  Account created but verification failed.\n\n"
                        "Please contact support to verify your email."
                    )
            else:
                # Development mode - show link in console
                print(f"\n🔗 VERIFICATION LINK FOR {email}:")
                print(verification_link if verification_link else "No link generated")
                print("\n⚠️  Paste this link in a browser to verify email.")

                return True, (
                    "🎉 Account created!\n\n"
                    "⚠️  DEVELOPMENT MODE: Email not configured.\n"
                    "Check console for verification link.\n\n"
                    f"📧 Email: {email}\n"
                    "Copy link from console and open in browser."
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
        Checks for email verification status.
        """
        try:
            # Fetch user by email
            user = auth.get_user_by_email(email)

            if not user.email_verified:
                # Offer to resend verification
                if self.email_enabled:
                    verification_link = self._generate_verification_link(email)
                    if verification_link:
                        self._send_verification_email(email, verification_link)
                        return False, (
                            "❌ Email not verified!\n\n"
                            "📧 A new verification email has been sent.\n"
                            "Please check your inbox and spam folder."
                        )

                return False, (
                    "❌ Email not verified!\n\n"
                    "Please check your email for the verification link.\n"
                    "Or contact support for assistance."
                )

            return True, "✅ Sign in successful! Welcome back!"

        except firebase_exceptions.NotFoundError:
            return False, "❌ Invalid email or password."

        except Exception as e:
            return False, f"❌ Error: {e}"

    def resend_verification_email(self, email):
        """Resends verification email."""
        try:
            user = auth.get_user_by_email(email)

            if user.email_verified:
                return True, "✅ Email is already verified!"

            verification_link = self._generate_verification_link(email)

            if verification_link:
                if self.email_enabled:
                    email_sent = self._send_verification_email(email, verification_link)
                    if email_sent:
                        return True, f"📧 Verification email resent to {email}"
                    else:
                        return False, "❌ Failed to send email"
                else:
                    print(f"\n🔗 RESEND VERIFICATION LINK FOR {email}:")
                    print(verification_link)
                    return True, "📧 Check console for verification link"
            else:
                return False, "❌ Failed to generate verification link"

        except firebase_exceptions.NotFoundError:
            return False, "❌ User not found"
        except Exception as e:
            return False, f"❌ Error: {e}"


# If you were to run this file alone for testing, you'd need to mock the QApplication:
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    if not QApplication.instance():
        app = QApplication(sys.argv)

    # Initialize the database manager for testing purposes
    try:
        db_manager = DatabaseManager()
        print("\nDatabaseManager initialized successfully.")

        # Test configuration
        print("\n" + "=" * 60)
        print("EMAIL CONFIGURATION TEST")
        print("=" * 60)

        if not db_manager.email_enabled:
            print("❌ Email is NOT configured")
            print("\nTo fix this, update EMAIL_CONFIG with:")
            print("1. Your Gmail address")
            print("2. An App Password from Google")
            print("\nGet App Password from: https://myaccount.google.com/apppasswords")
        else:
            print("✅ Email is configured")

            # Test email sending
            print("\nTesting email sending...")
            test_link = "https://example.com/verify?token=test123"
            success = db_manager._send_verification_email("test@example.com", test_link)
            if success:
                print("✅ Test email sent successfully!")
            else:
                print("❌ Test email failed")

        print("=" * 60)

    except SystemExit:
        print("Initialization failed due to missing key.")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")