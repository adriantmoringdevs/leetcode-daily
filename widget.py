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
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from pathlib import Path
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
        self.setFixedSize(350, 240)

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
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(8)

        # -------------------------
        # Top row
        # -------------------------
        header = QHBoxLayout()
        header.setSpacing(10)

        # LeetCode logo
        self.logo = QLabel()
        logo_path = Path(__file__).resolve().parent / "leetcode_logo_transparent.png"
        pixmap = QPixmap(str(logo_path))
        self.logo.setPixmap(
            pixmap.scaled(
                42,
                50,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        self.logo.setFixedSize(42, 50)

        # Title
        self.title = QLabel("LeetCode Daily")
        self.title.setStyleSheet("""
            QLabel {
                color: #111111;
                font-size: 17px;
                font-weight: 600;
            }
        """)

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.clicked.connect(self.close)

        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888;
                border: none;
                font-size: 20px;
                padding: 0px;
            }

            QPushButton:hover {
                color: white;
            }
        """)

        header.addWidget(self.logo)
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.close_button)

        # -------------------------
        # Status
        # -------------------------
        self.status = QLabel()
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #111111;
                font-size: 24px;
                font-weight: 600;
            }
        """)

        # -------------------------
        # Problem
        # -------------------------
        self.problem = QLabel()
        self.problem.setAlignment(Qt.AlignCenter)
        self.problem.setWordWrap(True)
        self.problem.setStyleSheet("""
            QLabel {
                color: #1c1c1c;
                font-size: 15px;
                font-weight: 400;
            }
        """)

        # -------------------------
        # Time
        # -------------------------
        self.time = QLabel()
        self.time.setAlignment(Qt.AlignCenter)
        self.time.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 13px;
            }
        """)

        # -------------------------
        # Open LeetCode button
        # -------------------------
        self.open_button = QPushButton("Open LeetCode")
        self.open_button.setFixedHeight(34)
        self.open_button.clicked.connect(self.open_leetcode)

        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #4a4d52;
                color: white;
                border: 1px solid #5b5f65;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #5a5e64;
            }

            QPushButton:pressed {
                background-color: #41444a;
            }
        """)

        # -------------------------
        # Layout
        # -------------------------
        layout.addLayout(header)
        layout.addSpacing(4)
        layout.addWidget(self.status)
        layout.addWidget(self.problem)
        layout.addWidget(self.time)
        layout.addStretch()
        layout.addWidget(self.open_button)

        self.setLayout(layout)

        # -------------------------
        # Widget appearance
        # -------------------------
        self.setStyleSheet("""
            QWidget {
                background-color: #3b3e42;
                font-family: Arial;
            }
        """)

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
