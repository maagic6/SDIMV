import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QWidget, QGridLayout,QLineEdit,QPushButton, QLabel, QTextEdit, QListWidget, QVBoxLayout, QFrame, QMenu, QListWidgetItem, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon, QAction, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
from Image import ImageProcess
from icon import resource_path

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #window size
        self.setWindowTitle('SD Image Metadata Viewer')
        self.setGeometry(100, 100, 400, 200)

        #ui components
        self.image_preview = QLabel()
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
        self.file_list.setMinimumWidth(300)

        self.view_metadata_button = QPushButton('View')
        self.view_metadata_button.clicked.connect(self.view_metadata)

        self.selected_file = QLineEdit()

        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.clear_list_button = QPushButton('Clear')
        self.clear_list_button.clicked.connect(self.clear_file_list)

        github_link = QLabel('<a href="https://github.com/maagic6/sd_image">GitHub</a>')
        github_link.setOpenExternalLinks(True)
        
        version_label = QLabel('Version 1.0.1')
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        #layout
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()
        bottom_layout = QHBoxLayout()
        bottom_left_layout = QHBoxLayout()
        bottom_right_layout = QHBoxLayout()
        layout.addLayout(grid_layout)
        layout.addLayout(bottom_layout)
        bottom_layout.addLayout(bottom_left_layout)
        bottom_layout.addLayout(bottom_right_layout)
        grid_layout.addWidget(self.file_list, 1, 0, 1, 3)
        grid_layout.addWidget(self.view_metadata_button, 2, 0)
        grid_layout.addWidget(self.browse_button, 2, 1)
        grid_layout.addWidget(self.clear_list_button, 2, 2)
        grid_layout.addWidget(QLabel('Selected file:'), 3, 0)
        grid_layout.addWidget(self.selected_file, 3, 1, 1, 5)
        grid_layout.addWidget(self.image_preview_frame, 1, 3, 1, 2)
        bottom_left_layout.addWidget(github_link)
        bottom_right_layout.addWidget(version_label)

        #set stretch factors
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)

        #set alignments
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bottom_left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bottom_right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

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

        for row, (label_text, widget, widget_name) in enumerate(self.widget_info):
            label = QLabel(label_text)
            setattr(self, widget_name, widget)
            widget.setReadOnly(True)
            grid_layout.addWidget(label, row+4, 0, 1, 5)
            grid_layout.addWidget(widget, row+4, 1, 1, 5)

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
                            widget.setText(str(image.getRaw()))
                        else:
                            widget.setText(data[key])

    def show_context_menu(self, event):
        menu = QMenu(self)
        add_action = QAction("Add", self)
        add_action.triggered.connect(self.open_file_dialog)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.remove_selected_item)
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_file_list)
        menu.addAction(add_action)
        menu.addAction(remove_action)
        menu.addAction(clear_action)
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.view_metadata()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = resource_path("icon/emu.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    sys.exit(app.exec())