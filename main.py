import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Import the Database Manager (to instantiate the connection)
from database_manager import DatabaseManager

# Import the Main Window class (which we assume is defined in sign_in_up.py)
from sign_in_up import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Enable High DPI scaling and set style
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setStyle("Fusion")

    # 1. Initialize the Database Manager
    db_manager_instance = DatabaseManager()

    # 2. Instantiate the main window, passing the manager
    # This assumes MainWindow is structured to accept db_manager in its constructor.
    window = MainWindow(db_manager=db_manager_instance, initial_form="signup")

    # Show the window and start the application loop
    window.show()
    sys.exit(app.exec_())