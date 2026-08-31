import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget
)

from leetcode import solved_today

class LeetCodeWidget(QWidget):
    def __init__(self, username):
        super().__init__()

        self.username = username

        self.setWindowTitle("Leetcode Daily")

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("LEETCODE DAILY")
        status = QLabel(self.get_status())

        layout.addWidget(title)
        layout.addWidget(status)


        self.setLayout(layout)

    def get_status(self):
        if solved_today(self.username):
            return "🟢 You solved a problem today!"
        else:
            return "🔴 You haven't solved a problem today."