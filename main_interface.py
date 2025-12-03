import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize


# --- Custom Widget for a single Project Card ---
class ProjectCard(QWidget):
    def __init__(self, title, description, date):
        super().__init__()

        # Give the widget an object name for QSS styling
        self.setObjectName("ProjectCard")

        # Set a fixed size for uniformity
        self.setFixedSize(280, 160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        # 1. Top Section (Icon and Delete Button)
        top_layout = QHBoxLayout()

        # Database Icon
        icon_label = QLabel()
        # NOTE: You must have an image named 'database_icon.png' in the same directory
        icon_label.setPixmap(QPixmap("database_icon.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setStyleSheet("padding: 5px; background-color: #F3E8FF; border-radius: 8px;")

        # Delete Button (Initially hidden/faint, styled in QSS)
        self.delete_btn = QPushButton()
        self.delete_btn.setObjectName("DeleteButton")
        # NOTE: You must have an image named 'trash_icon.png' for the button icon
        self.delete_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))  # Fallback icon
        self.delete_btn.setIconSize(QSize(20, 20))
        self.delete_btn.setFixedSize(30, 30)

        # Use QSS to style and handle hover state visibility/color

        top_layout.addWidget(icon_label)
        top_layout.addStretch(1)
        top_layout.addWidget(self.delete_btn)

        layout.addLayout(top_layout)

        # 2. Project Details
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #6A6A6A;")
        layout.addWidget(desc_label)

        # Spacer to push the date to the bottom
        layout.addSpacing(10)

        # Date
        date_label = QLabel(f"📅 {date}")
        date_label.setStyleSheet("color: #6A6A6A; font-size: 11pt;")
        layout.addWidget(date_label)

        layout.addStretch(1)


# --- The Main Application Window ---
class DataForgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # NOTE: Window title is set by the calling AuthAppContainer
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.apply_styles()
        self.create_header()

        # Container for the main content (Projects or Empty State)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.main_layout.addWidget(self.content_container)

        # Simulate having projects for the initial view
        self.has_projects = True

        if self.has_projects:
            self.show_projects()
        else:
            self.show_empty_state()

    # --- Header Bar ---
    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(10)

        # Logo
        logo_label = QLabel("DataForge")
        logo_label.setObjectName("Logo")
        header_layout.addWidget(logo_label)

        header_layout.addStretch(1)

        # Settings Button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setObjectName("SettingsButton")
        settings_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(settings_btn)

        # Sign Out Button
        sign_out_btn = QPushButton("Sign Out")
        sign_out_btn.setObjectName("SignOutButton")
        sign_out_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(sign_out_btn)

        self.main_layout.addWidget(header_widget)

        # Add a subtle separator below the header
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #E0E0E0;")
        self.main_layout.addWidget(separator)

    # --- Content State: Projects ---
    def show_projects(self):
        # Clear previous content
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.widget() is not None:
                item.widget().setParent(None)
            elif item.layout() is not None:
                # Handle nested layouts if necessary (though not strictly needed here)
                pass


        # Main Title and New Project Button
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 10, 20, 10)

        title_label = QLabel("Your Projects")
        title_label.setObjectName("PageTitle")
        title_layout.addWidget(title_label)

        title_layout.addStretch(1)

        new_project_btn = QPushButton("+ New Project")
        new_project_btn.setObjectName("NewProjectButton")
        new_project_btn.setCursor(Qt.PointingHandCursor)
        title_layout.addWidget(new_project_btn)

        self.content_layout.addWidget(title_bar)

        subtitle_label = QLabel("Create and manage your data generation projects")
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setContentsMargins(20, 0, 20, 10)
        self.content_layout.addWidget(subtitle_label)

        # Project Grid
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(20)

        # Add sample project cards (based on your image)
        projects = [
            ("7567575", "7567567", "12/3/2025"),
            ("75757", "757575", "12/3/2025"),
            ("5676765", "7575757", "12/3/2025"),
            ("dan", "test", "11/8/2025"),
        ]

        # Populate the grid (2 columns)
        for i, (title, desc, date) in enumerate(projects):
            row = i // 2
            col = i % 2
            card = ProjectCard(title, desc, date)
            grid_layout.addWidget(card, row, col)

        # Add an empty column spacer to push items left
        grid_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)
        grid_layout.setRowStretch(len(projects) // 2 + 1, 1)  # Push content to top

        self.content_layout.addWidget(grid_widget)
        self.content_layout.addStretch(1)

    # --- Content State: Empty State (No Projects) ---
    def show_empty_state(self):
        # Clear previous content
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.widget() is not None:
                item.widget().setParent(None)
            elif item.layout() is not None:
                pass


        # Title bar (same as project view, just for context)
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 10, 20, 10)

        title_label = QLabel("Your Projects")
        title_label.setObjectName("PageTitle")

        title_layout.addWidget(title_label)
        title_layout.addStretch(1)

        new_project_btn = QPushButton("+ New Project")
        new_project_btn.setObjectName("NewProjectButton")
        new_project_btn.setCursor(Qt.PointingHandCursor)
        title_layout.addWidget(new_project_btn)

        self.content_layout.addWidget(title_bar)

        # Subtitle
        subtitle_label = QLabel("Create and manage your data generation projects")
        subtitle_label.setObjectName("PageSubtitle")
        subtitle_label.setContentsMargins(20, 0, 20, 10)
        self.content_layout.addWidget(subtitle_label)

        # Empty State Container (White box in the middle)
        empty_state_widget = QWidget()
        empty_state_widget.setObjectName("EmptyState")

        empty_layout = QVBoxLayout(empty_state_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(15)

        # Database Icon
        icon_label = QLabel()
        # NOTE: Using a scaled icon placeholder
        icon_label.setPixmap(QPixmap("database_icon.png").scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        empty_layout.addWidget(icon_label, alignment=Qt.AlignCenter)

        # No Projects Yet text
        no_projects_label = QLabel("No projects yet")
        no_projects_label.setFont(QFont("Arial", 20, QFont.Bold))
        empty_layout.addWidget(no_projects_label, alignment=Qt.AlignCenter)

        # Sub-text
        create_first_label = QLabel("Create your first project to start generating data")
        create_first_label.setStyleSheet("color: #6A6A6A;")
        empty_layout.addWidget(create_first_label, alignment=Qt.AlignCenter)

        # Create Project Button
        create_btn = QPushButton("+ Create Project")
        create_btn.setObjectName("CreateProjectButton")
        create_btn.setCursor(Qt.PointingHandCursor)
        create_btn.setFixedSize(150, 40)
        empty_layout.addWidget(create_btn, alignment=Qt.AlignCenter)

        # Vertically center the empty state widget
        self.content_layout.addStretch(1)
        self.content_layout.addWidget(empty_state_widget)
        self.content_layout.addStretch(1)

    # --- Qt Style Sheets (QSS) for Aesthetics and Hover Effects ---
    def apply_styles(self):
        style = """
        /* --- General Window and Background --- */
        QMainWindow, QWidget {
            background-color: #F8F8F8;
            font-family: Arial, sans-serif;
        }

        /* --- Logo and Titles --- */
        #Logo {
            font-size: 24pt;
            font-weight: bold;
            color: #5D5D5D; /* Darker text */
        }
        #PageTitle {
            font-size: 20pt;
            font-weight: bold;
            padding-top: 10px;
        }
        #PageSubtitle {
            font-size: 11pt;
            color: #6A6A6A;
            padding-left: 20px;
            padding-bottom: 10px;
        }

        /* --- Header Buttons --- */
        #SettingsButton {
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            padding: 8px 15px;
            color: #5D5D5D;
        }
        #SettingsButton:hover {
            background-color: #F0F0F0; /* Light hover */
        }

        #SignOutButton, #NewProjectButton, #CreateProjectButton {
            background-color: #A995C9; /* Default purple */
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 15px;
            font-weight: bold;
        }
        #SignOutButton:hover, #NewProjectButton:hover, #CreateProjectButton:hover {
            background-color: #8C7BA9; /* Darker purple on hover */
        }

        /* --- Project Card Styles --- */
        #ProjectCard {
            background-color: white;
            border-radius: 10px;
            /* Using border for a subtle card look, as true box-shadow requires advanced techniques */
            border: 1px solid #E0E0E0; 
        }
        #ProjectCard:hover {
            border: 1px solid #A995C9; /* Highlight border on hover */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Simulate shadow */
        }

        /* --- Delete Button on Card Hover (Image_fe35a0.png) --- */
        #DeleteButton {
            background: transparent;
            border: none;
            /* Initially faint icon - setting the image directly can be complex, so we'll style the background on hover */
        }
        #DeleteButton:hover {
            background-color: #A995C9; /* Purple square on hover */
            border-radius: 5px;
            /* You would typically swap to a white trash icon here for contrast */
            /* This example uses a standard system icon, which may not change color */
        }

        /* --- Empty State Container --- */
        #EmptyState {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #E0E0E0;
            min-height: 350px;
            margin: 20px;
        }
        """
        self.setStyleSheet(style)


# Define MainInterface as an alias for your main application class
class MainInterface(DataForgeApp):
    pass