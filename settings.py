import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class SettingsForm(QWidget):
    def __init__(self):
        super().__init__()
        # Set window size to be adaptive
        # Starting size is arbitrary; the minimum size governs practical viewing
        self.setWindowTitle("Settings - Data Generator")

        # Set minimum window size to prevent too small display
        self.setMinimumSize(800, 600)

        self.setStyleSheet(self.get_main_style())
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header (64px height) ---
        header = self.create_header()
        main_layout.addWidget(header)

        # --- Content Area ---
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 40, 0, 40)  # Increased top/bottom margins for spacing
        content_layout.setSpacing(0)

        # --- 1. Title and Subtitle Block (Centered to 640px) ---

        # This widget is constrained to 640px width
        title_block = QWidget()
        title_block.setFixedWidth(640)

        # Vertical layout for the text elements inside the 640px block
        title_v_layout = QVBoxLayout(title_block)
        title_v_layout.setContentsMargins(0, 0, 0, 0)  # No internal margins
        title_v_layout.setSpacing(5)

        title = QLabel("Settings")
        self.title_label = title  # Retain reference for setter method
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)

        subtitle = QLabel("Manage your account settings and preferences")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignLeft)

        title_v_layout.addWidget(title)
        title_v_layout.addWidget(subtitle)

        # Horizontal wrapper to center the 640px title block
        title_h_wrapper = QHBoxLayout()
        title_h_wrapper.addStretch(1)
        title_h_wrapper.addWidget(title_block)
        title_h_wrapper.addStretch(1)

        content_layout.addLayout(title_h_wrapper)

        # Add vertical space between title and first form card
        content_layout.addSpacing(30)  # Increased spacing from 20 to 30

        # --- 2. Forms Area (Centered) ---
        forms_container = QWidget()
        forms_layout = QVBoxLayout(forms_container)
        forms_layout.setContentsMargins(0, 0, 0, 0)
        # Added explicit spacing between the two form cards
        forms_layout.setSpacing(20)

        # --- 2.1 Profile Information Card (640x318) ---
        profile_card = self.create_profile_card()
        profile_card.setFixedHeight(318)  # Fixed height as requested
        profile_card.setFixedWidth(640)  # Fixed width as requested
        forms_layout.addWidget(profile_card)

        # --- 2.2 Account Actions Card (640x134) ---
        actions_card = self.create_actions_card()
        actions_card.setFixedHeight(134)  # Fixed height as requested
        actions_card.setFixedWidth(640)  # Fixed width as requested
        forms_layout.addWidget(actions_card)

        # Add a stretch at the bottom of the forms container to keep content grouped at the top
        forms_layout.addStretch(1)

        # Center the forms container
        forms_wrapper = QHBoxLayout()
        forms_wrapper.addStretch(1)
        forms_wrapper.addWidget(forms_container)
        forms_wrapper.addStretch(1)
        content_layout.addLayout(forms_wrapper)

        main_layout.addWidget(content_wrapper)

        # Add a stretch at the bottom of the main content area
        main_layout.addStretch(1)

    # --- Removed the following methods as they are no longer needed for centering:
    # def update_title_position(self):
    # def resizeEvent(self, event):
    # ---

    def create_header(self):
        """Create the header with back button"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(64)

        header_layout = QHBoxLayout(header)
        # Increased left margin from 40 to 60 for slight right shift
        header_layout.setContentsMargins(60, 0, 20, 0)  # Left and right margins

        # Back to Dashboard button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setObjectName("backButton")
        back_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(back_btn)

        # Add stretch to push button to the left
        header_layout.addStretch()

        return header

    def create_input_field(self, label_text, placeholder, icon_char):
        """Creates a labeled input with an icon prefix."""
        container = QVBoxLayout()
        container.setSpacing(2)  # Reduced spacing
        container.setContentsMargins(0, 0, 0, 0)
        container.setAlignment(Qt.AlignLeft)  # Align elements to the left

        # Label with Icon
        label = QLabel(f"{icon_char} {label_text}")
        label.setObjectName("inputLabel")
        label.setAlignment(Qt.AlignLeft)  # Align label to the left
        container.addWidget(label)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setObjectName("mainInput")
        line_edit.setProperty("isEditable", True)
        line_edit.setFixedSize(590, 40)  # Fixed size as requested
        line_edit.setAlignment(Qt.AlignLeft)  # Align text in input to the left

        container.addWidget(line_edit)
        return container

    def create_read_only_field(self, label_text, value, icon_char, hint_text=""):
        """Creates a labeled read-only field."""
        container = QVBoxLayout()
        container.setSpacing(2)  # Reduced spacing
        container.setContentsMargins(0, 0, 0, 0)
        container.setAlignment(Qt.AlignLeft)  # Align field

        # Label with Icon
        label = QLabel(f"{icon_char} {label_text}")
        label.setObjectName("inputLabel")
        label.setAlignment(Qt.AlignLeft)  # Align label to the left
        container.addWidget(label)

        read_only_edit = QLineEdit(value)
        read_only_edit.setReadOnly(True)
        read_only_edit.setObjectName("readOnlyInput")
        read_only_edit.setProperty("isEditable", False)
        read_only_edit.setFixedSize(590, 40)  # Fixed size as requested
        read_only_edit.setAlignment(Qt.AlignLeft)  # Align text in input to the left

        container.addWidget(read_only_edit)

        if hint_text:
            hint = QLabel(hint_text)
            hint.setObjectName("hintText")
            hint.setAlignment(Qt.AlignLeft)  # Align hint to the left
            container.addWidget(hint)

        return container

    def create_profile_card(self):
        card = QFrame()
        card.setObjectName("cardFrame")

        layout = QVBoxLayout(card)
        # Adjusted margins: 640 - 590 (input width) = 50. 50/2 = 25px horizontal padding/margin
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(10)  # Increased spacing for better look
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Keep content aligned to top and centered horizontally

        card_title = QLabel("Profile Information")
        card_title.setObjectName("cardTitle")
        card_title.setAlignment(Qt.AlignLeft)  # Align card title to the left
        layout.addWidget(card_title)

        layout.addSpacing(10)  # Space after title (Increased from 5)

        # Full Name Input
        name_layout = self.create_input_field("Full Name", "damian", "👤")
        layout.addLayout(name_layout)

        layout.addSpacing(15)  # Space between inputs (Increased from 10)

        # Email Address Input
        email_layout = self.create_read_only_field(
            "Email Address",
            "danyisrael720@gmail.com",
            "✉️",
            "Changing your email will require confirmation"
        )
        layout.addLayout(email_layout)

        # Update Profile Button
        update_btn = QPushButton("Update Profile")
        update_btn.setObjectName("updateButton")
        update_btn.setCursor(Qt.PointingHandCursor)
        update_btn.setFixedSize(590, 40)  # Fixed button size
        update_btn.setStyleSheet("text-align: center;")  # Center button text

        layout.addSpacing(20)  # Space before button (Increased from 15)
        layout.addWidget(update_btn)

        layout.addStretch(1)  # Stretch at the bottom to maintain height

        return card

    def create_actions_card(self):
        card = QFrame()
        card.setObjectName("signoutCardFrame")

        layout = QVBoxLayout(card)
        # Adjusted margins: 640 - 590 (input width) = 50. 50/2 = 25px horizontal padding/margin
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(10)  # Spacing
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Keep content aligned to top and centered horizontally

        card_title = QLabel("Account Actions")
        card_title.setObjectName("cardTitle")
        card_title.setAlignment(Qt.AlignLeft)  # Align card title to the left
        layout.addWidget(card_title)

        layout.addSpacing(10)  # Space after title (Increased from 5)

        # Sign Out Button
        # Text without arrow
        signout_btn = QPushButton("Sign Out")
        signout_btn.setObjectName("signoutButton")
        signout_btn.setCursor(Qt.PointingHandCursor)
        signout_btn.setFixedSize(590, 40)  # Fixed button size
        signout_btn.setStyleSheet("text-align: center;")  # Center button text

        layout.addSpacing(20)  # Space before button (Increased from 15)
        layout.addWidget(signout_btn)

        layout.addStretch(1)  # Stretch at the bottom to maintain height

        return card

    def set_title_text(self, text):
        """Method to set the title text"""
        self.title_label.setText(text)

    def get_main_style(self):
        # Color Palette
        P_PURPLE = "#A383D4"  # Primary/Update Button (Violet)
        P_RED = "#E55353"  # Danger/Signout Button
        P_LIGHT_BG = "#F9F9FB"  # Main window background
        P_CARD_BG = "white"  # Card background
        P_TEXT_DARK = "#333333"
        P_TEXT_MEDIUM = "#666666"

        return f"""
            QWidget {{
                background-color: {P_LIGHT_BG};
                color: {P_TEXT_DARK};
                font-family: Arial;
            }}

            /* --- Header --- */
            #header {{
                background-color: {P_CARD_BG};
                border-bottom: 1px solid #E0E0E0;
            }}

            /* --- Typography --- */
            #title {{
                font-size: 28px;
                font-weight: bold;
                color: {P_TEXT_DARK};
                margin-bottom: 0px;
            }}
            #subtitle {{
                font-size: 14px;
                color: {P_TEXT_MEDIUM};
                margin-bottom: 0px;
            }}
            #cardTitle {{
                font-size: 18px;
                font-weight: bold;
                color: {P_TEXT_DARK};
                margin-bottom: 0px;
            }}
            #inputLabel {{
                font-size: 13px;
                font-weight: bold;
                color: {P_TEXT_DARK};
                margin-bottom: 2px;
                background-color: white; /* Ensures labels match the white card background */
                padding: 0px; /* Added to ensure no inherited padding causes gray borders */
            }}
            #hintText {{
                font-size: 11px;
                color: {P_TEXT_MEDIUM};
                margin-top: 2px;
                background-color: white; /* Ensures hint text background matches the white card */
                padding: 0px; /* Added to ensure no inherited padding causes gray borders */
            }}

            /* --- Layout Cards --- */
            #cardFrame {{
                background-color: {P_CARD_BG};
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }}
            #signoutCardFrame {{
                background-color: {P_CARD_BG};
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }}

            /* --- Inputs --- */
            QLineEdit {{
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                text-align: left;
            }}

            /* Read-only fields - Confirmed background is white */
            #readOnlyInput {{
                background-color: white;
                color: {P_TEXT_MEDIUM};
            }}

            /* Editable field focus style */
            QLineEdit[isEditable="true"]:focus {{
                border: 2px solid {P_PURPLE};
                padding: 9px 11px;
            }}

            /* --- Buttons --- */
            #backButton {{
                background-color: transparent;
                border: none;
                color: {P_TEXT_MEDIUM};
                font-size: 14px; 
                padding: 8px 15px; 
                border-radius: 6px; 
                text-align: left;
                font-weight: bold; 
            }}
            #backButton:hover {{
                background-color: {P_PURPLE}; 
                color: white; 
                text-decoration: none; 
                font-weight: bold; 
            }}

            #updateButton {{
                background-color: {P_PURPLE};
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
                border: none;
                border-radius: 10px;
                text-align: center;
            }}
            #updateButton:hover {{
                background-color: #8D67B2;
            }}

            /* --- Sign Out Button (Danger) Styling --- */
            /* Normal State: White background, Red text, Red border */
            #signoutButton {{
                background-color: white;
                color: {P_RED};
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
                border: 1px solid {P_RED}; 
                border-radius: 10px; 
                text-align: center;
            }}
            /* Hover State: Purple background (matching update button color), White text */
            #signoutButton:hover {{
                background-color: #A383D4; /* Used explicit hex code for robustness */
                color: white;
                border: 1px solid #A383D4; /* Match border to hover background */
            }}
        """


