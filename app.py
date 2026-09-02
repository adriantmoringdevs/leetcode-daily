import sys 
from config import load_username, save_username
from PySide6.QtWidgets import QApplication
from widget import LeetCodeWidget

username = load_username()

if username is None:
    username = input("Enter your Leetcode username: ")
    save_username(username)

app = QApplication(sys.argv)

widget = LeetCodeWidget(username)

widget.show()
widget.make_desktop_widget()

sys.exit(app.exec())