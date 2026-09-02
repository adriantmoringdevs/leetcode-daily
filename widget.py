from datetime import datetime, timedelta
import subprocess
from pync import Notifier
import objc
from AppKit import NSApp
from AppKit import NSWindow
from Quartz import CGWindowLevelForKey, kCGDesktopWindowLevelKey
from AppKit import (
    NSWindowCollectionBehaviorStationary,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSDockWindowLevel,
)

import objc
from ctypes import c_void_p


from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from leetcode import todays_submissions


class LeetCodeWidget(QWidget):

    def __init__(self, username):
        super().__init__()

        self.username = username
        self.last_notification = None

        self.setWindowFlags(
        Qt.FramelessWindowHint
        )

        self.setWindowTitle("Leetcode Daily")
        self.setFixedSize(300, 200)

        self.setStyleSheet("""
    QWidget {
        background-color: #f7f7f7;
        font-family: Arial;
    }

    QLabel {
        color: #222;
    }

    QPushButton {
        background-color: #222;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
    }

    QPushButton:hover {
        background-color: #444;
    }
""")

        self.setup_ui()
        # self.make_desktop_widget()

        # TIMER TO UPDATE API CALL 
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(30 * 60 * 1000)

    def make_desktop_widget(self):
        window = self.windowHandle()
        native_window = window.winId()

        ns_view = objc.objc_object(c_void_p=native_window)
        ns_window = ns_view.window()

        behavior = (
            NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorCanJoinAllSpaces
        )

        ns_window.setCollectionBehavior_(behavior)

        ns_window.setLevel_(-1)

        print("Window level:", ns_window.level())
        print("Collection behavior:", ns_window.collectionBehavior())
        print("Dock level:", NSDockWindowLevel)

    def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPosition().toPoint()


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_position = event.globalPosition().toPoint()
            delta = new_position - self.drag_position

            self.move(self.pos() + delta)

            self.drag_position = new_position

    def send_notification(self):
        now = datetime.now()

        if (
            self.last_notification is None
            or now - self.last_notification >= timedelta(hours=2)
        ):
            Notifier.notify(
                "You haven't solved a LeetCode problem today!",
                title="LeetCode Daily"
            )

        self.last_notification = now

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Top row
        header = QHBoxLayout()

        self.title = QLabel("LEETCODE DAILY")
        self.title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                font-size: 18px;
                padding: 0px;
            }

            QPushButton:hover {
                color: #222;
            }
        """)

        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.close_button)

        # Main content
        self.status = QLabel()
        self.status.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        self.problem = QLabel()
        self.problem.setStyleSheet("""
            font-size: 13px;
        """)

        self.time = QLabel()
        self.time.setStyleSheet("""
            font-size: 12px;
            color: #666;
        """)

        self.open_button = QPushButton("Open LeetCode")
        self.open_button.setMinimumHeight(35)
        self.open_button.clicked.connect(self.open_leetcode)

        layout.addLayout(header)
        layout.addWidget(self.status, alignment=Qt.AlignCenter)
        layout.addWidget(self.problem, alignment=Qt.AlignCenter)
        layout.addWidget(self.time, alignment=Qt.AlignCenter)
        layout.addWidget(self.open_button)

        self.setLayout(layout)

        self.refresh_status()


    def refresh_status(self):
        print("Checking LeetCode...")

        try:
            submissions = todays_submissions(self.username)

        except Exception as error:
            print(f"LeetCode check failed: {error}")

            self.status.setText("⚠️ CHECK FAILED")
            self.problem.setText("Couldn't reach LeetCode.")
            self.time.setText("Will try again later.")
            return

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

            self.send_notification()



    def open_leetcode(self):
        QDesktopServices.openUrl(
            QUrl("https://leetcode.com/problemset/")
        )
