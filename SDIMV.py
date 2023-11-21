import sys, subprocess, qdarkstyle
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from pathlib import Path
from qframelesswindow import FramelessWindow, StandardTitleBar
from Image import ImageProcess
from icon import resource_path

class EditableLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            self.focusNextPrevChild(True)
        else:
            super().keyPressEvent(event)

class EditableTextEdit(QTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            event.ignore()
        else:
            super().keyPressEvent(event)

class ZoomableGraphicsView(QGraphicsView):
    def wheelEvent(self, event: QWheelEvent):
        event.accept()
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

class CustomListWidget(QListWidget):
    def wheelEvent(self, event: QWheelEvent):
        current_index = self.currentRow()
        total_items = self.count()
        if total_items == 0:
            return
        new_index = (current_index - 1) % total_items if event.angleDelta().y() > 0 else (current_index + 1) % total_items
        self.setCurrentRow(new_index)

class CustomTitleBar(StandardTitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn.setHoverColor(Qt.GlobalColor.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.GlobalColor.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.minBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.maxBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.closeBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    
class MainWindow(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        #window size
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowTitle('SD Image Metadata Viewer')
        self.titleBar.raise_()
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        self.resize(640,820)
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        #self.setGeometry(100, 100, 640, 820)
        self.setMinimumWidth(480)
        icon_path = resource_path("icon/emu.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.image_preview_frame = QFrame()
        self.image_preview_frame.setFrameShape(QFrame.Shape.Box)
        self.image_preview_frame.setLineWidth(1)
        self.image_preview_frame.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.image_frame = QVBoxLayout(self.image_preview_frame)

        self.image_scene = QGraphicsScene()
        self.image_view = ZoomableGraphicsView(self.image_scene)
        self.image_view.setRenderHint(QPainter.Antialiasing, True)
        self.image_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.image_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.image_frame.addWidget(self.image_view)
     
        self.file_list = CustomListWidget()
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemSelectionChanged.connect(self.handle_item_selection_changed)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(self.image_preview_frame)
        self.splitter.setSizes([1,2])
        self.splitter.splitterMoved.connect(self.update_image)

        self.selected_file = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.browse_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clear_list_button = QPushButton('Clear')
        self.clear_list_button.clicked.connect(self.clear_file_list)
        self.clear_list_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        github_link = QLabel('<a href="https://github.com/maagic6/SDIMV">GitHub</a>')
        github_link.setOpenExternalLinks(True)
        
        version_label = QLabel('Version 1.1.0')
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        #layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,30,0,0)
        bottom_half = QWidget(self)
        grid_layout = QGridLayout(bottom_half)
        bottom_layout = QHBoxLayout()
        bottom_left_layout = QHBoxLayout()
        bottom_right_layout = QHBoxLayout()

        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.splitter)
        self.v_splitter.addWidget(bottom_half)
        self.v_splitter.splitterMoved.connect(self.update_image)

        layout.addWidget(self.v_splitter)
        layout.addLayout(bottom_layout)
        bottom_layout.addLayout(bottom_left_layout)
        bottom_layout.addLayout(bottom_right_layout)
        #grid_layout.addWidget(self.splitter, 1, 0, 1, 3)
        #grid_layout.addWidget(self.view_metadata_button, 3, 3)
        grid_layout.addWidget(self.browse_button, 2, 1)
        grid_layout.addWidget(self.clear_list_button, 2, 0)
        #grid_layout.addWidget(self.folder_button, 3, 4)
        grid_layout.addWidget(QLabel('Selected file:'), 3, 0)
        grid_layout.addWidget(self.selected_file, 3, 1, 1, 5)
        self.widget_info = [
            ('Positive prompt:', EditableTextEdit(), 'prompt'),
            ('Negative prompt:', EditableTextEdit(), 'nprompt'),
            ('Steps:', EditableLineEdit(), 'steps'),
            ('Sampler:', EditableLineEdit(), 'sampler'),
            ('CFG scale:', EditableLineEdit(), 'cfg_scale'),
            ('Seed:', EditableLineEdit(), 'seed'),
            ('Size:', EditableLineEdit(), 'size'),
            ('Model hash:', EditableLineEdit(), 'model_hash'),
            ('Model:', EditableLineEdit(), 'model'),
            ('LoRA:', EditableLineEdit(), 'lora'),
            ('Raw:', EditableTextEdit(), 'raw')
        ]

        for row, (label_text, widget, widget_name) in enumerate(self.widget_info):
            label = QLabel(label_text)
            setattr(self, widget_name, widget)
            #widget.setReadOnly(True)
            grid_layout.addWidget(label, row+4, 0, 1, 5)
            grid_layout.addWidget(widget, row+4, 1, 1, 5)
        #grid_layout.addWidget(self.image_preview_frame, 1, 3, 1, 2)
        bottom_left_layout.addWidget(github_link)
        github_link.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        #bottom_right_layout.addWidget(settings_button)
        bottom_right_layout.addWidget(version_label)
        version_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        #set stretch factors
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setColumnStretch(3, 1)
        grid_layout.setColumnStretch(4, 1)
        self.v_splitter.setStretchFactor(0, 3)
        self.v_splitter.setStretchFactor(1, 1)
        bottom_half.setMinimumHeight(400)

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
            "Select image files",
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
        self.image_scene.clear()
        self.selected_file.clear()
        for _, widget, _ in self.widget_info:
            widget.clear()

    def view_metadata(self, item):
        selected_item = item
        if selected_item:
            selected_index = self.file_list.row(selected_item)
            selected_file = self.selected_files[selected_index]
            self.selected_file.setText(selected_file)

            if Path(selected_file).exists():
                pixmap = QPixmap(selected_file)
                self.image_scene.clear()
                self.image_scene.addPixmap(pixmap)
                self.image_view.resetTransform()
                self.image_scene.setSceneRect(QRectF(pixmap.rect()))
                self.image_view.setScene(self.image_scene)
                self.image_view.fitInView(self.image_scene.sceneRect(), Qt.KeepAspectRatio)

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
                self.image_scene.clear()
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()

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

    def update_image(self):
        self.image_view.fitInView(self.image_scene.sceneRect(), Qt.KeepAspectRatio)

def launch():
    app = QApplication(sys.argv)
    window_id = 'application'
    shared_mem_id = 'sharedmemid'
    semaphore = QSystemSemaphore(window_id, 1)
    semaphore.acquire()
    if sys.platform != 'win32':
        nix_fix_shared_mem = QSharedMemory(shared_mem_id)
        if nix_fix_shared_mem.attach():
            nix_fix_shared_mem.detach()
    shared_memory = QSharedMemory(shared_mem_id)
    if shared_memory.attach():  # attach a copy of the shared memory, if successful, the application is already running
        is_running = True
    else:
        shared_memory.create(1)  # allocate a shared memory block of 1 byte
        is_running = False

    semaphore.release()

    if is_running:  # if the application is already running, show the warning message
        QMessageBox.warning(None, 'Application already running', 'One instance of the application is already running.')
        return
    
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    icon_path = resource_path("icon/emu.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    launch()