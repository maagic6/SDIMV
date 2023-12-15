from qframelesswindow import FramelessDialog
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from icon import resource_path

class AboutDialog(FramelessDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 0)
        logo = QLabel()
        icon = resource_path("icon/icon.ico")
        pixmap = QPixmap(icon)
        pixmap = pixmap.scaledToWidth(80)
        logo.setPixmap(pixmap)
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        title = QLabel("SDIMV")
        title.setFont(font)
        githubLink = QLabel('<a href="https://github.com/maagic6/SDIMV">GitHub</a>')
        githubLink.setOpenExternalLinks(True)
        vlayout.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop)
        vlayout.addWidget(QLabel("v1.2.1"), alignment=Qt.AlignmentFlag.AlignTop)
        vlayout.addWidget(githubLink, alignment=Qt.AlignmentFlag.AlignBottom)
        hlayout.addWidget(logo)
        hlayout.addLayout(vlayout)
        layout.addLayout(hlayout)
        self.setFixedSize(240,120)
        self.setContentsMargins(0,0,35,0)
        self.setWindowTitle("About")
    
    def closeEvent(self, event):
        self.main_window.setEnabled(True)
        self.deleteLater()
        event.accept()

    def showEvent(self, event):
        main_window_center = self.main_window.geometry().center()
        self.move(main_window_center - self.rect().center())
        super().showEvent(event)