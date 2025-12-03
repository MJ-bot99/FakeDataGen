import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QSizePolicy,
    QSpacerItem, QLineEdit, QMenu  # QMenu is needed for the custom dropdown functionality
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QPoint  # QPoint is needed for positioning the menu


class PreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Generator - Schema Builder")
        self.setGeometry(100, 100, 1440, 1024)
        self.setStyleSheet(self._get_main_style())

        # Instance variables for dynamic content
        self.schema_layout = None  # Will hold the QVBoxLayout of the schema card
        self.field_widgets = []  # List to track all dynamically added field rows

        self._setup_ui()

    # --- Field Creation Logic ---
    def _create_field_row(self):
        """Creates a single QWidget containing the Field Name, Field Type (Custom Dropdown), and Delete Button."""
        field_row_widget = QWidget()
        field_row_layout = QHBoxLayout(field_row_widget)
        field_row_layout.setContentsMargins(0, 0, 0, 0)
        field_row_layout.setSpacing(10)

        # Field Name Input
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g. username, email")
        field_row_layout.addWidget(name_input, 2)  # Takes 2 parts of stretch

        # --- REPLACING QComboBox with Composite Custom Dropdown ---
        type_group_widget = QWidget()
        # Layout for blending QLineEdit and QPushButton seamlessly
        type_group_layout = QHBoxLayout(type_group_widget)
        type_group_layout.setContentsMargins(0, 0, 0, 0)
        type_group_layout.setSpacing(0)

        # 1. The actual display input (read-only)
        type_display = QLineEdit()
        type_display.setText("Full Name")
        type_display.setReadOnly(True)
        type_display.setObjectName("typeDisplay")

        # 2. The dropdown button with the arrow icon
        dropdown_button = QPushButton("▼")
        dropdown_button.setFixedSize(QSize(40, 40))
        dropdown_button.setObjectName("dropdownButton")
        dropdown_button.setCursor(Qt.PointingHandCursor)

        type_group_layout.addWidget(type_display)
        type_group_layout.addWidget(dropdown_button)

        field_row_layout.addWidget(type_group_widget, 2)

        # Store references on the row widget so the handler can access the right elements
        field_row_widget.type_display_ref = type_display
        field_row_widget.dropdown_button_ref = dropdown_button

        # Connect the button to the custom menu handler
        # We pass the parent row widget so the handler knows which field to update
        dropdown_button.clicked.connect(lambda checked: self._handle_open_type_dropdown(field_row_widget))
        # -------------------------------------------------------------------------

        # Delete Button
        delete_button = QPushButton("🗑️")
        delete_button.setObjectName("deleteFieldButton")
        delete_button.setFixedSize(QSize(40, 40))
        field_row_layout.addWidget(delete_button, 0)

        # Connect delete button to remove the row
        delete_button.clicked.connect(lambda: self._delete_field_row(field_row_widget))

        return field_row_widget

    # --- Custom Dropdown Handlers ---

    def _update_field_type(self, type_display_widget, type_name):
        """Updates the text in the QLineEdit display with the selected type."""
        type_display_widget.setText(type_name)

    def _handle_open_type_dropdown(self, field_row_widget):
        """Handles the click on the dropdown button by showing a QMenu."""
        menu = QMenu(self)

        # Define field types content
        field_types = [
            "Full Name",
            "Email Address",
            "Phone Number",
            "Street Address",
            "Date of Birth"
        ]

        type_display_widget = field_row_widget.type_display_ref
        dropdown_button = field_row_widget.dropdown_button_ref

        for type_name in field_types:
            action = menu.addAction(type_name)
            # Crucial: pass both the selected type name AND the specific display widget to update
            action.triggered.connect(lambda checked, t=type_name, d=type_display_widget: self._update_field_type(d, t))

        # Position the menu right below the dropdown button
        # mapToGlobal converts the button's local coordinates to screen coordinates
        point = dropdown_button.mapToGlobal(QPoint(0, dropdown_button.height()))
        menu.exec_(point)

    # --- Dynamic Field Management ---

    def add_new_field(self):
        """Creates a new field row and adds it to the schema layout."""
        if not self.schema_layout:
            print("Error: Schema layout not initialized.")
            return

        new_field_widget = self._create_field_row()
        self.field_widgets.append(new_field_widget)

        # Insert the new widget before the last two items: the QSpacerItem (spacer) and the QHBoxLayout (save row)
        insert_index = self.schema_layout.count() - 2
        self.schema_layout.insertWidget(insert_index, new_field_widget)

    def _delete_field_row(self, widget_to_remove):
        """Removes a field row widget from the layout and cleans up."""
        widget_to_remove.setParent(None)  # Remove widget from its parent
        self.field_widgets.remove(widget_to_remove)
        widget_to_remove.deleteLater()  # Schedule for deletion

    # --- UI Setup ---
    def _setup_ui(self):
        # --- 1. Main Container Widget ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # We'll use a main vertical layout for the entire page content
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Define the width for content alignment
        CONTENT_WIDTH = 1000

        # --- 2. Header Bar ---
        header_bar = QWidget()
        header_bar.setObjectName("header")
        header_bar.setFixedHeight(64)

        outer_header_layout = QHBoxLayout(header_bar)
        outer_header_layout.setContentsMargins(0, 0, 0, 0)
        outer_header_layout.setSpacing(0)

        inner_header_content = QWidget()
        inner_header_content.setFixedWidth(CONTENT_WIDTH)

        header_layout = QHBoxLayout(inner_header_content)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        left_header_content = QVBoxLayout()
        left_header_content.setSpacing(0)
        left_header_content.setContentsMargins(0, 10, 0, 0)

        back_label = QLabel("←")
        back_label.setFont(QFont("Arial", 16))

        schema_id_label = QLabel("75757")
        schema_id_label.setObjectName("headerTitle")

        schema_sub_label = QLabel("75757")
        schema_sub_label.setObjectName("hintText")

        id_row_layout = QHBoxLayout()
        id_row_layout.setSpacing(5)
        id_row_layout.addWidget(back_label)
        id_row_layout.addWidget(schema_id_label)
        id_row_layout.addStretch(1)

        left_header_content.addLayout(id_row_layout)
        left_header_content.addWidget(schema_sub_label)

        header_layout.addLayout(left_header_content)
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        preview_button = QPushButton("◎ Preview")
        preview_button.setObjectName("previewButton")
        header_layout.addWidget(preview_button)

        outer_header_layout.addStretch(1)
        outer_header_layout.addWidget(inner_header_content)
        outer_header_layout.addStretch(1)

        main_layout.addWidget(header_bar)

        # --- 3. Main Content Area (Schema Builder) ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 40, 0, 40)
        content_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        content_layout.setSpacing(30)

        # --- 3.1. Schema Builder Title and Add Field Button ---
        title_container = QWidget()
        title_container.setFixedWidth(CONTENT_WIDTH)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_group = QVBoxLayout()
        schema_title_label = QLabel("Schema Builder")
        schema_title_label.setObjectName("mainTitle")

        schema_subtitle_label = QLabel("Define the fields for your fake data")
        schema_subtitle_label.setObjectName("subTitle")

        title_group.addWidget(schema_title_label)
        title_group.addWidget(schema_subtitle_label)

        title_layout.addLayout(title_group)
        title_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        add_field_button = QPushButton("+ Add Field")
        add_field_button.setObjectName("primaryButton")
        add_field_button.setFixedSize(QSize(150, 40))

        # CONNECT THE BUTTON HERE
        add_field_button.clicked.connect(self.add_new_field)

        title_layout.addWidget(add_field_button)

        content_layout.addWidget(title_container, alignment=Qt.AlignHCenter)

        # --- 3.2. Field Definition Card ---
        schema_card = QWidget()
        schema_card.setObjectName("schemaCard")
        schema_card.setFixedWidth(CONTENT_WIDTH)

        schema_layout = QVBoxLayout(schema_card)
        self.schema_layout = schema_layout  # Store reference
        schema_layout.setSpacing(20)
        schema_layout.setContentsMargins(40, 30, 40, 30)

        # Field Header Row (Index 0)
        field_header_layout = QHBoxLayout()
        field_header_layout.addWidget(QLabel("Field Name"))
        field_header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        field_header_layout.addWidget(QLabel("Field Type"))
        field_header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        field_header_layout.setStretch(0, 2)
        field_header_layout.setStretch(2, 2)
        schema_layout.addLayout(field_header_layout)

        # --- Initial Field Row (Will be added dynamically by the method) ---
        self.add_new_field()  # Call to create the first field row

        # Spacer before Save button (Index count - 2)
        spacer_item = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        schema_layout.addItem(spacer_item)

        # Save Schema Button (Aligned right) (Index count - 1)
        save_button = QPushButton("Save Schema")
        save_button.setObjectName("primaryButton")
        save_button.setFixedSize(QSize(180, 40))

        save_row_layout = QHBoxLayout()
        save_row_layout.addStretch(1)
        save_row_layout.addWidget(save_button)

        schema_layout.addLayout(save_row_layout)

        content_layout.addWidget(schema_card, alignment=Qt.AlignHCenter)

        # Add final stretch
        content_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        main_layout.addWidget(content_widget)

    def _get_main_style(self):
        # Color Palette
        P_PURPLE = "#A383D4"  # Primary/Update Button (Violet)
        P_LIGHT_BG = "#F9F9FB"  # Main window background
        P_CARD_BG = "white"  # Card background
        P_TEXT_DARK = "#333333"  # Very dark text for high contrast
        P_TEXT_MEDIUM = "#666666"
        P_DANGER_RED = "#E55353"  # Danger red color
        P_LIGHT_PURPLE = "#C5A3E8"  # Lighter purple for Add/Save buttons
        P_LIGHT_GRAY = "#F8F8F8"  # Light background for the button part

        # FIX: Use an f-string (f"""...""") for the entire return value and ensure proper indentation.
        return f"""
            /* --- Window and General Styling --- */
            QMainWindow {{
                background-color: {P_LIGHT_BG};
            }}
            #header {{
                background-color: {P_CARD_BG};
                border-bottom: 1px solid #D0D0D0;
            }}
            #schemaCard {{
                background-color: {P_CARD_BG};
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}

            /* --- Titles and Labels --- */
            #headerTitle {{
                font-size: 20px;
                font-weight: bold;
                color: {P_TEXT_DARK};
            }}
            #mainTitle {{
                font-size: 30px;
                font-weight: bold;
                color: {P_TEXT_DARK};
            }}
            #subTitle {{
                font-size: 16px;
                color: {P_TEXT_MEDIUM};
            }}

            /* --- Buttons --- */
            #primaryButton {{
                background-color: {P_PURPLE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            #primaryButton:hover {{
                background-color: {P_LIGHT_PURPLE};
            }}
            #previewButton {{
                background-color: white;
                color: {P_TEXT_DARK};
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 14px;
            }}
            #previewButton:hover {{
                background-color: {P_LIGHT_GRAY};
            }}

            /* --- Standard Input Fields (QLineEdit) --- */
            QLineEdit {{
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 14px;
                background-color: white;
            }}

            /* --- CUSTOM DROPDOWN QSS (Revised Modern Look) --- */

            /* 1. Style for the main display part (QLineEdit) */
            #typeDisplay {{
                /* Keep all borders from QLineEdit default, but remove right border for blending */
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-right: none;
                background-color: white;
            }}

            /* 2. Style for the dropdown button (QPushButton) */
            #dropdownButton {{
                background-color: white; /* Clean white background */
                border: 1px solid #D0D0D0;
                /* Match the text input style except for left border and corners to blend */
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-left: none; /* Blend with QLineEdit */
                padding: 0;
                font-size: 14px;
                font-weight: bold;
                color: {P_PURPLE}; /* Use primary purple for the arrow */
            }}
            #dropdownButton:hover {{
                background-color: {P_LIGHT_GRAY}; /* Subtle hover effect */
                color: {P_PURPLE};
            }}
            /* ----------------------------------------------------- */

            /* --- QMenu/Dropdown Menu Styling (Updated for modern look) --- */
            QMenu {{
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                padding: 5px; /* Padding around the items */
            }}

            QMenu::item {{
                padding: 8px 15px; /* Increased padding for better touch/click targets */
                border-radius: 4px;
                color: {P_TEXT_DARK};
                font-size: 14px;
            }}

            QMenu::item:selected {{
                background-color: {P_PURPLE}; /* Primary color on hover/selection */
                color: white;
            }}
            /* ----------------------------------------------------- */


            /* --- Delete Button (Trash Icon) --- */
            #deleteFieldButton {{
                background-color: transparent;
                border: 1px solid #D0D0D0;
                border-radius: 6px;
                font-size: 16px;
                color: {P_DANGER_RED};
            }}
            #deleteFieldButton:hover {{
                background-color: #FEE;
                border: 1px solid {P_DANGER_RED};
            }}

            /* --- Hint Text (Small secondary text) --- */
            #hintText {{
                font-size: 11px;
                color: {P_TEXT_MEDIUM};
            }}

            /* --- General Text (Ensuring QLabels default to the dark color) --- */
            QLabel {{
                font-family: Arial;
                color: {P_TEXT_DARK};
                font-size: 14px;
            }}
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PreviewWindow()
    window.show()
    sys.exit(app.exec_())