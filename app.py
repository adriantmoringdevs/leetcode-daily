import sys 

from PySide6.QtWidgets import QApplication

from widget import LeetCodeWidget

username = input("Enter your Leetcode username:")

app = QApplication(sys.argv)

widget = LeetCodeWidget(username)

widget.show()

sys.exit(app.exec())