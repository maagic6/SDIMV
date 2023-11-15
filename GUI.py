import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QGridLayout,QLineEdit,QPushButton, QLabel, QTextEdit
from PyQt6.QtGui import QIcon
from pathlib import Path
from Image import ImageProcess
from icon import resource_path

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('SD Image Metadata')
        self.setGeometry(100, 100, 500, 200)

        layout = QGridLayout()
        self.setLayout(layout)

        file_browse = QPushButton('Browse')
        file_browse.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()
        self.prompt = QTextEdit()
        self.prompt.setMaximumHeight(200)
        self.prompt.setReadOnly(True)
        self.nprompt = QTextEdit()
        self.nprompt.setMaximumHeight(200)
        self.nprompt.setReadOnly(True)
        self.steps = QLineEdit()
        self.steps.setReadOnly(True)
        self.sampler = QLineEdit()
        self.sampler.setReadOnly(True)
        self.cfg_scale = QLineEdit()
        self.cfg_scale.setReadOnly(True)
        self.seed = QLineEdit()
        self.seed.setReadOnly(True)
        layout.addWidget(QLabel('File:'), 0, 0)
        layout.addWidget(self.filename_edit, 0, 1)
        layout.addWidget(file_browse, 0 ,2)
        layout.addWidget(QLabel('Positive prompt:'), 1, 0)
        layout.addWidget(self.prompt, 1, 1)
        layout.addWidget(QLabel('Negative prompt:'), 2, 0)
        layout.addWidget(self.nprompt, 2, 1)
        layout.addWidget(QLabel('Steps:'), 3, 0)
        layout.addWidget(self.steps, 3, 1)
        layout.addWidget(QLabel('Sampler:'), 4, 0)
        layout.addWidget(self.sampler, 4, 1)
        layout.addWidget(QLabel('CFG scale:'), 5, 0)
        layout.addWidget(self.cfg_scale, 5, 1)
        layout.addWidget(QLabel('Seed:'), 6, 0)
        layout.addWidget(self.seed, 6, 1)
      
        self.show()


    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File", 
            "D:\\icons\\avatar\\", 
            "Images (*.png *.jpg)"
        )
        if filename:
            path = Path(filename)
            self.filename_edit.setText(str(path))

            with open(path, 'rb') as file:
                image = ImageProcess(file)
                prompt = image.positivePrompt()
                
                if prompt == -1:
                    self.prompt.setText('')
                    self.nprompt.setText('')
                    self.steps.setText('')
                    self.sampler.setText('')
                    self.cfg_scale.setText('')
                else:
                    data = image.getInfo()
                    self.prompt.setText(data["prompt"])
                    self.nprompt.setText(data["nprompt"])
                    self.steps.setText(data["steps"])
                    self.sampler.setText(data["sampler"])
                    self.cfg_scale.setText(data["cfg_scale"])
                    self.seed.setText(data["seed"])



if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = resource_path("icon/emu.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    sys.exit(app.exec())