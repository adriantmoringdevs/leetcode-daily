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
    NSDockWindowLevel
)

import objc
from ctypes import c_void_p


from PySide6.QtCore import QTimer, QUrl, Qt, QSettings
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QColor
from pathlib import Path
from leetcode import todays_submissions


class LeetCodeWidget(QWidget):

    def __init__(self, username):
        super().__init__()

        self.username = username
        self.last_notification = None

        # Frameless + translucent background is required for the rounded
        # corners in the stylesheet to actually render (otherwise Qt paints
        # a square window behind the rounded QSS background).
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle("LeetCode Daily")
        self.setFixedSize(300, 220)

        # Real widgets stay where you last put them, even after a relaunch.
        self.settings = QSettings("AdrianMoring", "LeetCodeWidget")
        self._restore_position()
        self._desktop_widget_configured = False

        self.setup_ui()

        # TIMER TO UPDATE API CALL
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(30 * 60 * 1000)

    def _restore_position(self):
        saved_pos = self.settings.value("widget_pos", None)
        if saved_pos is not None:
            self.move(saved_pos)
        else:
            self.move(60, 60)

    def showEvent(self, event):
        super().showEvent(event)
        # windowHandle()/winId() only resolve to a real native window once
        # the widget has actually been shown, so this can't run from
        # __init__ - it has to happen here, and only once.
        if not self._desktop_widget_configured:
            self._desktop_widget_configured = True
            self.make_desktop_widget()

    def make_desktop_widget(self):
        # Turn the whole app into a background "accessory": no Dock icon,
        # doesn't appear in Cmd+Tab, doesn't steal focus on launch. This is
        # what makes it read as a widget instead of a regular app window.
        NSApp.setActivationPolicy_(1)

        window = self.windowHandle()
        if window is None:
            return

        native_window = window.winId()
        ns_view = objc.objc_object(c_void_p=int(native_window))
        ns_window = ns_view.window()

        # Stay fixed across Spaces/Mission Control switches, and show on
        # every Space rather than just the one it was opened on.
        behavior = (
            NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorCanJoinAllSpaces
        )
        ns_window.setCollectionBehavior_(behavior)

        # Sit just above the desktop wallpaper/icons and below every normal
        # app window, so anything else you open always draws on top of it.
        desktop_level = CGWindowLevelForKey(kCGDesktopWindowLevelKey)
        ns_window.setLevel_(-1)

        # The QSS drop-shadow on the card already gives it depth; a native
        # window shadow on top of that looks like a doubled, boxy outline.
        ns_window.setHasShadow_(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_position = event.globalPosition().toPoint()
            delta = new_position - self.drag_position

            self.move(self.pos() + delta)

            self.drag_position = new_position

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.settings.setValue("widget_pos", self.pos())

    def closeEvent(self, event):
        self.settings.setValue("widget_pos", self.pos())
        super().closeEvent(event)

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
        # -------------------------
        # Card container
        # -------------------------
        # Everything visible lives inside `self.card`, a child widget sized
        # to the window. This lets us drop a soft drop-shadow on it (Qt can't
        # apply a QGraphicsDropShadowEffect to a widget and paint its own
        # rounded background at the same time without clipping issues).
        self.card = QWidget(self)
        self.card.setGeometry(0, 0, self.width(), self.height())
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QWidget#card {
                background: qlineargradient(
                    x1:0, y1:0, x2:0.4, y2:1,
                    stop:0 #232a3d,
                    stop:0.55 #161b28,
                    stop:1 #0c0f18
                );
                border-radius: 26px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(22, 18, 22, 20)
        layout.setSpacing(6)

        # -------------------------
        # Top row
        # -------------------------
        header = QHBoxLayout()
        header.setSpacing(10)

        # LeetCode logo, in a small tinted circle like the weather glyph
        self.logo_wrap = QWidget()
        self.logo_wrap.setFixedSize(34, 34)
        self.logo_wrap.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 17px;
            }
        """)
        logo_layout = QVBoxLayout(self.logo_wrap)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignCenter)

        self.logo = QLabel()
        logo_path = Path(__file__).resolve().parent / "leetcode_logo_transparent.png"
        pixmap = QPixmap(str(logo_path))
        self.logo.setPixmap(
            pixmap.scaled(20, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        logo_layout.addWidget(self.logo)

        # Title
        self.title = QLabel("LeetCode")
        self.title.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.55);
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 1px;
                background: transparent;
            }
        """)

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(22, 22)
        self.close_button.clicked.connect(self.close)
        self.close_button.setCursor(Qt.PointingHandCursor)

        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.35);
                border: none;
                font-size: 18px;
                padding: 0px;
            }

            QPushButton:hover {
                color: rgba(255, 255, 255, 0.85);
            }
        """)

        header.addWidget(self.logo_wrap)
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.close_button, alignment=Qt.AlignTop)

        # -------------------------
        # Status (the big "16°"-style number)
        # -------------------------
        self.status = QLabel()
        self.status.setAlignment(Qt.AlignLeft)
        self._set_status_color("#f5f6fa")

        # -------------------------
        # Problem
        # -------------------------
        self.problem = QLabel()
        self.problem.setAlignment(Qt.AlignLeft)
        self.problem.setWordWrap(True)
        self.problem.setStyleSheet("""
            QLabel {
                color: #B3B3B3;;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)

        # -------------------------
        # Time
        # -------------------------
        self.time = QLabel()
        self.time.setAlignment(Qt.AlignLeft)
        self.time.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.4);
                font-size: 12px;
                background: transparent;
            }
        """)

        # -------------------------
        # Open LeetCode button
        # -------------------------
        self.open_button = QPushButton("Open LeetCode")
        self.open_button.setFixedHeight(36)
        self.open_button.setCursor(Qt.PointingHandCursor)
        self.open_button.clicked.connect(self.open_leetcode)

        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #f5f6fa;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
            }

            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.06);
            }
        """)

        # -------------------------
        # Layout
        # -------------------------
        layout.addLayout(header)
        layout.addSpacing(6)
        layout.addWidget(self.status)
        layout.addWidget(self.problem)
        layout.addWidget(self.time)
        layout.addStretch()
        layout.addWidget(self.open_button)

        self.refresh_status()

    def _set_status_color(self, hex_color):
        self.status.setStyleSheet(f"""
            QLabel {{
                color: {hex_color};
                font-size: 36px;
                font-weight: 700;
                background: transparent;
            }}
        """)

    def refresh_status(self):
        print("Checking LeetCode...")

        try:
            submissions = todays_submissions(self.username)

        except Exception as error:
            print(f"LeetCode check failed: {error}")

            self.status.setText("⚠️")
            self.problem.setText("Couldn't reach LeetCode.")
            self.time.setText("Will try again later.")
            return

        if submissions:
            latest_submission = submissions[0]

            self.status.setText("Done")
            self._set_status_color("#B3B3B3")
            self.problem.setText(latest_submission["title"])

            solved_time = datetime.fromtimestamp(
                int(latest_submission["timestamp"])
            ).strftime("%I:%M %p")

            self.time.setText(f"Solved at {solved_time}")

        else:
            self.status.setText("Not done")
            self._set_status_color("#B3B3B3")
            self.problem.setText("You haven't solved a problem today.")
            self.time.setText("")

            self.send_notification()

    def open_leetcode(self):
        QDesktopServices.openUrl(
            QUrl("https://leetcode.com/problemset/")
        )