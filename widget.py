from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from leetcode import todays_submissions


class LeetCodeWidget(QWidget):

    def __init__(self, username):
        super().__init__()

        self.username = username

        self.setWindowTitle("Leetcode Daily")

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

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.problem)
        layout.addWidget(self.time)

        self.setLayout(layout)

        self.refresh_status()

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