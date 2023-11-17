import sys, subprocess
from PyQt6.QtWidgets import QApplication, QFileDialog, QWidget, QGridLayout,QLineEdit,QPushButton, QLabel, QTextEdit, QListWidget, QVBoxLayout, QFrame, QMenu, QListWidgetItem, QHBoxLayout, QToolButton
from PyQt6.QtGui import QPixmap, QIcon, QAction, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
from pathlib import Path
from itertools import chain
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
        self.image_preview_frame.setMinimumSize(200,300)
        self.image_preview_frame.setLineWidth(1)
        self.image_frame = QVBoxLayout(self.image_preview_frame)
        self.image_frame.addWidget(self.image_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.view_metadata)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.setMinimumWidth(300)
        self.file_list.itemSelectionChanged.connect(self.handle_item_selection_changed)

        self.selected_file = QLineEdit()

        #self.view_metadata_button = QPushButton('View')
        #self.view_metadata_button.clicked.connect(self.open_image)
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.clear_list_button = QPushButton('Clear')
        self.clear_list_button.clicked.connect(self.clear_file_list)
        #self.folder_button = QPushButton('Open folder')
        #self.folder_button.clicked.connect(self.open_folder)

        github_link = QLabel('<a href="https://github.com/maagic6/SDIMV">GitHub</a>')
        github_link.setOpenExternalLinks(True)
        
        version_label = QLabel('Version 1.0.4')
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
        #grid_layout.addWidget(self.view_metadata_button, 3, 3)
        grid_layout.addWidget(self.browse_button, 2, 1)
        grid_layout.addWidget(self.clear_list_button, 2, 0)
        #grid_layout.addWidget(self.folder_button, 3, 4)
        grid_layout.addWidget(QLabel('Selected file:'), 3, 0)
        grid_layout.addWidget(self.selected_file, 3, 1, 1, 5)
        grid_layout.addWidget(self.image_preview_frame, 1, 3, 1, 2)
        bottom_left_layout.addWidget(github_link)
        bottom_right_layout.addWidget(version_label)

        #set stretch factors
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setColumnStretch(3, 1)
        grid_layout.setColumnStretch(4, 1)

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
            ('LoRA:', QLineEdit(), 'lora'),
            ('Raw:', QTextEdit(), 'raw')
        ]

        for row, (label_text, widget, widget_name) in enumerate(self.widget_info):
            label = QLabel(label_text)
            setattr(self, widget_name, widget)
            widget.setReadOnly(True)
            grid_layout.addWidget(label, row+4, 0, 1, 5)
            grid_layout.addWidget(widget, row+4, 1, 1, 5)

        self.show()

        if len(sys.argv) > 1:
            new_files = []
            for arg in sys.argv[1:]:
                file_path = Path(arg)
                if file_path.is_dir():
                    new_files.extend(self.get_image_files_from_folder(file_path))
                elif str(file_path).replace('\\', '/') not in self.selected_files:
                    new_files.append(str(file_path).replace('\\', '/'))

            self.selected_files.extend(new_files)
            self.update_file_list()

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
        if self.file_list.count() > 0:
            self.file_list.clear()
            for file_path in self.selected_files:
                item = QListWidgetItem(file_path)
                self.file_list.addItem(item)
        else:
            self.file_list.clear()
            for file_path in self.selected_files:
                item = QListWidgetItem(file_path)
                self.file_list.addItem(item)
            first_item = self.file_list.item(0)
            self.file_list.setCurrentItem(first_item)
            self.view_metadata(first_item)

    def clear_file_list(self):
        self.selected_files = []
        self.update_file_list()
        self.image_preview.clear()
        self.selected_file.clear()
        for _, widget, _ in self.widget_info:
            widget.clear()

    def view_metadata(self, item):
        selected_item = item
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            selected_file = self.selected_files[selected_index]
            self.selected_file.setText(selected_file)
            pixmap = QPixmap(selected_file)
            self.image_preview.setPixmap(pixmap.scaledToWidth(self.image_preview_frame.width(), Qt.TransformationMode.FastTransformation))

            if Path(selected_file).exists():
                pixmap = QPixmap(selected_file)
                self.image_preview.setPixmap(pixmap.scaledToWidth(self.image_preview_frame.width(), Qt.TransformationMode.FastTransformation))

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
            else:
                self.image_preview.clear()
                self.selected_file.clear()
                for _, widget, _ in self.widget_info:
                    widget.clear()
                self.remove_selected_item()

    def show_context_menu(self, event):
        menu = QMenu(self)
        view_action = QAction("View", self)
        view_action.triggered.connect(self.open_image)
        openfolder_action = QAction("Open folder", self)
        openfolder_action.triggered.connect(self.open_folder)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.remove_selected_item)
        menu.addAction(view_action)
        menu.addAction(openfolder_action)
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
            new_files = []
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if Path(file_path).is_dir():
                    new_files.extend(self.get_image_files_from_folder(file_path))
                elif file_path not in self.selected_files:
                    new_files.append(file_path)
            print(new_files)

            self.selected_files.extend(new_files)
            self.update_file_list()
            event.acceptProposedAction()

    def get_image_files_from_folder(self, folder_path):
        folder_path = Path(folder_path)
        png_files = list(folder_path.rglob('*.[pP][nN][gG]'))
        jpg_files = list(folder_path.rglob('*.[jJ][pP][gG]'))
        png_files = [str(file_path).replace('\\', '/') for file_path in png_files]
        jpg_files = [str(file_path).replace('\\', '/') for file_path in jpg_files]
        image_files = set(png_files + jpg_files)
        unique_image_files = list(image_files - set(self.selected_files))

        return unique_image_files

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.view_metadata(self.file_list.currentItem())
    
    def handle_item_selection_changed(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            if 0 <= selected_index < len(self.selected_files):
                self.view_metadata(selected_item)

    def open_folder(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            selected_file = self.selected_files[selected_index]
            folder_path = Path(selected_file).parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))

    def open_image(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            selected_file = self.selected_files[selected_index]
            subprocess.run(['start', '', selected_file], shell=True)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = resource_path("icon/emu.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    sys.exit(app.exec())