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
        self.widget_info = [
            ('Positive prompt:', QTextEdit(), 'prompt'),
            ('Negative prompt:', QTextEdit(), 'nprompt'),
            ('Steps:', QLineEdit(), 'steps'),
            ('Sampler:', QLineEdit(), 'sampler'),
            ('CFG scale:', QLineEdit(), 'cfg_scale'),
            ('Seed:', QLineEdit(), 'seed'),
            ('Size:', QLineEdit(), 'size'),
            ('Model hash:', QLineEdit(), 'model_hash'),
            ('Model:', QLineEdit(), 'model'),
        ]
        layout.addWidget(QLabel('File:'), 0, 0)
        layout.addWidget(self.filename_edit, 0, 1)
        layout.addWidget(file_browse, 0 ,2)
        for row, (label_text, widget, widget_name) in enumerate(self.widget_info):
            label = QLabel(label_text)
            setattr(self, widget_name, widget)  # Set widget as an attribute of the class
            widget.setReadOnly(True)  # Set widget properties if needed
            layout.addWidget(label, row+1, 0)
            layout.addWidget(widget, row+1, 1)
      
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
                    for _, widget, _ in self.widget_info:
                        widget.setText('')
                else:
                    data = image.getInfo()
                    for _, widget, key in self.widget_info:
                        widget.setText(data[key])



if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = resource_path("icon/emu.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    sys.exit(app.exec())