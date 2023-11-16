import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QGridLayout,QLineEdit,QPushButton, QLabel, QTextEdit, QListWidget, QVBoxLayout, QFrame, QMenu, QListWidgetItem
from PyQt6.QtGui import QPixmap, QIcon, QAction, QStandardItemModel, QStandardItem
from PyQt6.QtCore import QSize, Qt
from pathlib import Path
from Image import ImageProcess
from icon import resource_path

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('SD Image Metadata')
        #self.setFixedSize(480, 720)
        self.setGeometry(100, 100, 400, 200)

        # UI components
        
        self.image_preview = QLabel()
        #self.image_preview.setGeometry(50,40,250,250)
        self.image_preview_frame = QFrame()
        self.image_preview_frame.setFrameShape(QFrame.Shape.Box)
        self.image_preview_frame.setFixedSize(200,300)
        self.image_preview_frame.setLineWidth(1)
        self.image_frame = QVBoxLayout(self.image_preview_frame)
        self.image_frame.addWidget(self.image_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.view_metadata)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.view_metadata_button = QPushButton('View Metadata')
        self.view_metadata_button.clicked.connect(self.view_metadata)
        #self.filename_edit = QLineEdit()
        self.selected_file = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.clear_list_button = QPushButton('Clear List')
        self.clear_list_button.clicked.connect(self.clear_file_list)

        # Layout
        layout = QGridLayout(self)
        #layout.addWidget(QLabel('Selected Images:'), 0, 0)
        layout.addWidget(self.file_list, 1, 0, 1, 3)
        layout.addWidget(self.view_metadata_button, 2, 0)
        layout.addWidget(self.clear_list_button, 2, 1)
        layout.addWidget(QLabel('Selected File:'), 3, 0)
        layout.addWidget(self.selected_file, 3, 1, 1, 5)
        layout.addWidget(self.image_preview_frame, 1, 3, 1, 2)
        #layout.addWidget(self.browse_button, 4, 0, 1, 2)

        #set stretch factors
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)  # This column will take twice as much space as the others

        #set alignments
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        #storage for selected file paths
        self.selected_files = []

        #enable drop events
        self.setAcceptDrops(True)

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
            ('Lora:', QLineEdit(), 'lora'),
            ('Raw:', QTextEdit(), 'raw')
        ]
        #layout.addWidget(self.filename_edit, 0, 1)
        layout.addWidget(self.browse_button, 2, 2)
        for row, (label_text, widget, widget_name) in enumerate(self.widget_info):
            label = QLabel(label_text)
            setattr(self, widget_name, widget)  # Set widget as an attribute of the class
            widget.setReadOnly(True)  # Set widget properties if needed
            layout.addWidget(label, row+4, 0, 1, 5)
            layout.addWidget(widget, row+4, 1, 1, 5)
      
        self.show()


    def open_file_dialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            "Images (*.png *.jpg)"
        )
        if filenames:
            unique_files = set(filenames) - set(self.selected_files)
            self.selected_files.extend(unique_files)
            self.update_file_list()

    def update_file_list(self):
        self.file_list.clear()
        for file_path in self.selected_files:
            item = QListWidgetItem(file_path)
            self.file_list.addItem(item)

    def clear_file_list(self):
        self.selected_files = []
        self.update_file_list()

    def view_metadata(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            selected_file = self.selected_files[selected_index]
            self.selected_file.setText(selected_file)

             # Display image preview
            pixmap = QPixmap(selected_file)
            self.image_preview.setPixmap(pixmap.scaledToWidth(self.image_preview_frame.width(), Qt.TransformationMode.FastTransformation))

            # Process the selected image and display metadata
            with open(selected_file, 'rb') as file:
                image = ImageProcess(file)
                prompt = image.positivePrompt()

                if prompt == -1:
                    for _, widget, _ in self.widget_info:
                        widget.setText('')
                else:
                    data = image.getInfo()
                    for _, widget, key in self.widget_info:
                        if key == 'raw':
                            widget.setText(image.getRaw())
                        else:
                            widget.setText(data[key])

    def show_context_menu(self, event):
        menu = QMenu(self)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.remove_selected_item)
        menu.addAction(remove_action)
        menu.exec(self.file_list.mapToGlobal(event))

    def remove_selected_item(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            del self.selected_files[selected_index]
            self.update_file_list()

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasUrls() and all(url.isLocalFile() for url in mime_data.urls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasUrls() and all(url.isLocalFile() for url in mime_data.urls()):
            new_files = [url.toLocalFile() for url in mime_data.urls() if url.toLocalFile() not in self.selected_files]
            self.selected_files.extend(new_files)
            self.update_file_list()
            event.acceptProposedAction()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = resource_path("icon/emu.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    sys.exit(app.exec())