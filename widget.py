from datetime import datetime

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from leetcode import todays_submissions


class LeetCodeWidget(QWidget):

    def __init__(self, username):
        super().__init__()

        self.username = username

        self.setWindowTitle("Leetcode Daily")
        self.setFixedSize(300, 180)

        self.setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(10 * 1000)

    def setup_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("LEETCODE DAILY")
        self.status = QLabel()
        self.problem = QLabel()
        self.time = QLabel() 

        self.open_button = QPushButton("Open LeetCode")
        self.open_button.clicked.connect(self.open_leetcode)

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.problem)
        layout.addWidget(self.time)
        layout.addWidget(self.open_button)

        self.setLayout(layout)

        self.refresh_status()

        self.setStyleSheet("""
                QWidget {
                    font-family: Arial;
                }

                QLabel {
                    padding: 4px;
                }

                QPushButton {
                    padding: 8px;
                }
            """)

    def refresh_status(self):
        print("Checking LeetCode...")

        submissions = todays_submissions(self.username)

        if submissions:
            latest_submission = submissions[0]

            self.status.setText("🟢 DONE TODAY")
            self.problem.setText(latest_submission["title"])

            solved_time = datetime.fromtimestamp(
                int(latest_submission["timestamp"])
            ).strftime("%I:%M %p")

            self.time.setText(f"Solved at {solved_time}")

        else:
            self.status.setText("🔴 NOT DONE")
            self.problem.setText(
                "You haven't solved a problem today."
            )
            self.time.setText("")

    def open_leetcode(self):
        QDesktopServices.openUrl(
            QUrl("https://leetcode.com/problemset/")
        )