import sys, subprocess, qdarkstyle
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QToolBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QScrollArea,
    QDockWidget,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QAction, QFont, QPainter, QMovie, QPixmap, QDesktopServices
from PyQt6.QtCore import Qt, QRectF, QEvent, QUrl, QSettings, QSystemSemaphore, QSharedMemory
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from pathlib import Path
from qframelesswindow import FramelessMainWindow
from image import ImageProcess
from file_handler import FileHandler
from custom_widgets import CustomDockWidget, CustomLineEdit, CustomTextEdit, CustomListWidget, CustomTitleBar, ZoomableGraphicsView
from icon import resource_path
from about_dialog import AboutDialog
    
class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self.initialized = False
        self.fileHandler = FileHandler(self)
        #window size
        self.setTitleBar(CustomTitleBar(self))
        self.setWindowTitle('SDIMV')
        self.titleBar.raise_()
        self.settings = QSettings("maagic6", "SDIMV")
        #self.settings.clear()
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        iconPath = resource_path("icon/icon.ico")
        self.setWindowIcon(QIcon(iconPath))

        toolbar = QToolBar("Toolbar")
        toolbar.setStyleSheet("QToolBar {background: transparent;}"
                              "QToolButton {background: transparent; border: none;}"
                              "QToolButton:hover {background: rgba(195, 195, 255, 50);}")
        iconPath2 = resource_path("icon/add.png")
        iconPath3 = resource_path("icon/remove.png")
        iconPath4 = resource_path("icon/clear.png")
        iconPath5 = resource_path("icon/about.png")
        addAction = QAction(QIcon(iconPath2), "Add", self)
        addAction.triggered.connect(self.fileHandler.openFileDialog)
        removeAction = QAction(QIcon(iconPath3), "Remove", self)
        removeAction.triggered.connect(self.fileHandler.removeSelectedItem)
        clearAction = QAction(QIcon(iconPath4), "Clear", self)
        clearAction.triggered.connect(self.fileHandler.clearFileList)
        aboutAction = QAction(QIcon(iconPath5), "About", self)
        aboutAction.triggered.connect(self.showAboutDialog)
        toolbar.addAction(addAction)
        toolbar.addAction(removeAction)
        toolbar.addAction(clearAction)
        toolbar.addAction(aboutAction)
        toolbar.setObjectName("Toolbar")
        self.addToolBar(toolbar)
        self.imagePreviewFrame = QFrame()
        self.imagePreviewFrame.setFrameShape(QFrame.Shape.Box)
        self.imagePreviewFrame.setLineWidth(1)
        self.imagePreviewFrame.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.imageFrame = QVBoxLayout()
        self.imagePreviewFrame.setLayout(self.imageFrame)

        self.imageScene = QGraphicsScene()
        self.imageView = ZoomableGraphicsView(self.imageScene)
        self.imageView.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.imageView.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.imageView.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.imageFrame.addWidget(self.imageView)
     
        self.fileList = CustomListWidget()
        self.fileList.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.fileList.customContextMenuRequested.connect(self.showContextMenu)
        self.fileList.itemSelectionChanged.connect(self.handleItemSelectionChanged)
        #self.fileList.setViewMode(CustomListWidget.ViewMode.IconMode)
        #self.fileList.setResizeMode(CustomListWidget.ResizeMode.Adjust)

        self.selectedFile = QLineEdit()
        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.fileHandler.openFileDialog)
        self.browseButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clearButton = QPushButton('Clear')
        self.clearButton.clicked.connect(self.fileHandler.clearFileList)
        self.clearButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        bottomHalf = QScrollArea(self)
        bottomHalf.setWidgetResizable(True)

        scrollContent = QWidget()
        self.gridLayout = QGridLayout(scrollContent)
        bottomHalf.setWidget(scrollContent)
        
        self.gridLayout.addWidget(QLabel('Selected file:'), 3, 0)
        self.gridLayout.addWidget(self.selectedFile, 4, 0, 1, 5)
        self.widgetInfo = [
            ('Positive prompt:', CustomTextEdit(), 'prompt'),
            ('Negative prompt:', CustomTextEdit(), 'negative_prompt'),
            ('Steps:', CustomLineEdit(), 'steps'),
            ('Sampler:', CustomLineEdit(), 'sampler'),
            ('CFG scale:', CustomLineEdit(), 'cfg_scale'),
            ('Seed:', CustomLineEdit(), 'seed'),
            ('Size:', CustomLineEdit(), 'size'),
            ('Model hash:', CustomLineEdit(), 'model_hash'),
            ('Model:', CustomLineEdit(), 'model'),
            ('LoRA:', CustomLineEdit(), 'lora'),
            ('Raw:', CustomTextEdit(), 'raw')
        ]

        for row, (label_text, widget, widget_name) in enumerate(self.widgetInfo):
            label = QLabel(label_text)
            setattr(self, widget_name + "_label", label)
            setattr(self, widget_name, widget)
            self.gridLayout.addWidget(label, 2*row+5, 0, 1, 5)
            self.gridLayout.addWidget(widget, 2*row+5+1, 0, 1, 5)


        # set stretch factors
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 1)
        self.gridLayout.setColumnStretch(4, 1)
        bottomHalf.setMinimumHeight(1)

        # set alignments
        self.gridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.gridLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.fileListWidget = CustomDockWidget(self)
        self.fileListWidget.setObjectName("FileListWidget")
        titleBarWidget = QWidget(self)
        titleBarLayout = QHBoxLayout(titleBarWidget)
        titleLabel = QLabel("File list")
        titleBarLayout.addWidget(titleLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        titleBarLayout.addStretch()
        titleBarLayout.addWidget(self.browseButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        titleBarLayout.addWidget(self.clearButton, alignment=Qt.AlignmentFlag.AlignHCenter)
        titleBarWidget.setMaximumHeight(10)
        self.fileListWidget.setWidget(self.fileList)
        self.fileListWidget.setWindowTitle("File list")
        self.fileList.setAcceptDrops(True)
        self.fileListWidget.setTitleBarWidget(titleLabel)
        self.fileListWidget.setAcceptDrops(True)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.fileListWidget)

        self.imageViewWidget = QDockWidget()
        self.imageViewWidget.setObjectName("ImageViewWidget")
        self.imageViewWidget.setWidget(self.imagePreviewFrame)
        self.imageViewWidget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.imagePreviewFrame.setAcceptDrops(True)
        self.imageView.setAcceptDrops(True)
        self.imageViewWidget.setTitleBarWidget(QLabel("Image view"))
        self.imageViewWidget.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
        self.imageViewWidget.setAcceptDrops(True)
        self.setCentralWidget(self.imageViewWidget)

        self.metadataWidget = QDockWidget()
        self.metadataWidget.setObjectName("MetadataWidget")
        self.metadataWidget.setWidget(bottomHalf)
        self.metadataWidget.setTitleBarWidget(QLabel("Metadata"))
        self.metadataWidget.setWindowTitle("Metadata")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.metadataWidget)
        self.setContentsMargins(0,30,0,0)
        self.isMediaPlayerDeleted = False
        self.isMovieDeleted = False

        self.fileList.verticalScrollBar().valueChanged.connect(self.fileHandler.lazyLoadIcon)
        self.fileListWidget.dockLocationChanged.connect(self.updateImageView)
        self.metadataWidget.dockLocationChanged.connect(self.updateImageView)
        self.fileListWidget.installEventFilter(self)
        self.imageViewWidget.installEventFilter(self)
        self.metadataWidget.installEventFilter(self)
        self.fileList.installEventFilter(self)
        self.installEventFilter(self)

        # load settings
        self.loadSettings()

        # enable drop events
        self.setAcceptDrops(True)

        self.show()
        self.initialized = True

        if len(sys.argv) > 1:
            new_files = []
            for arg in sys.argv[1:]:
                file_path = Path(arg)
                if file_path.is_dir():
                    new_files.extend(self.fileHandler.getFilesFromFolder(file_path))
                elif not self.fileHandler.isFileInList(str(file_path)):
                    new_files.append(str(file_path).replace('\\', '/'))

            self.fileHandler.updateFileList(new_files)

    def viewMetadata(self, item):
        if item:
            selectedFile = item.data(Qt.ItemDataRole.UserRole)
            self.selectedFile.setText(item.data(Qt.ItemDataRole.UserRole))

            if Path(selectedFile).exists():
                if selectedFile.lower().endswith(('.gif','.webp')):
                    self.cleanup()
                    self.movie = QMovie(selectedFile)
                    #self.imageScene.clear()
                    self.pixmap_item = QGraphicsPixmapItem()
                    self.imageScene.addItem(self.pixmap_item)
                    self.isMovieDeleted = False
                    self.imageView.resetTransform()
                    self.movie.start()
                    self.movie.frameChanged.connect(lambda: self.pixmap_item.setPixmap(self.movie.currentPixmap()))
                    self.imageScene.setSceneRect(QRectF(self.movie.currentPixmap().rect()))
                    self.imageView.setScene(self.imageScene)
                    self.imageView.fitInView(self.imageScene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                    self.imageView.resetZoom()
                elif selectedFile.lower().endswith(('.png', '.jpg', '.jpeg','.bmp')):
                    self.cleanup()
                    pixmap = QPixmap(selectedFile)
                    #self.imageScene.clear()
                    self.imageScene.addPixmap(pixmap)
                    self.imageView.setScene(self.imageScene)
                    self.imageView.resetTransform()
                    self.imageScene.setSceneRect(QRectF(pixmap.rect()))
                    self.imageView.fitInView(self.imageScene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
                    self.imageView.resetZoom()
                elif selectedFile.lower().endswith(('.mp4', '.mpeg4', '.avi')):
                    self.cleanup()
                    #self.imageScene.clear()
                    self.imageView.resetTransform()
                    self.media_player = QMediaPlayer()
                    self.video_item = QGraphicsVideoItem()
                    self.imageScene.addItem(self.video_item)
                    self.isMediaPlayerDeleted = False
                    self.media_player.setVideoOutput(self.video_item)
                    self.media_player.setSource(QUrl.fromLocalFile(selectedFile))
                    self.media_player.play()
                    self.media_player.mediaStatusChanged.connect(self.loopVideo)
                    self.video_item.nativeSizeChanged.connect(self.updateVideoView)
                    self.imageView.fitInView(self.imageScene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio) #workaround
                    self.imageView.resetZoom()
                with open(selectedFile, 'rb') as file:
                    image = ImageProcess(file)
                    prompt = image.positivePrompt()
                    if prompt == -1:
                        for _, widget, _ in self.widgetInfo:
                            widget.setText('')
                    else:
                        data = image.getInfo()
                        for _, widget, key in self.widgetInfo:
                            if key == 'raw':
                                widget.setText(str(image.getRaw()))
                            else:
                                widget.setText(str(data[key]))
            else:
                self.cleanup()
                #self.imageScene.clear()
                self.selectedFile.clear()
                for _, widget, _ in self.widgetInfo:
                    widget.clear()
                self.fileHandler.removeSelectedItem()
        else:
            self.cleanup()
            self.imageScene.clear()
            self.selectedFile.clear()
            for _, widget, _ in self.widgetInfo:
                widget.clear()

    def loopVideo(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
        else:
            pass
    
    def cleanup(self):
        if hasattr(self, 'movie') and self.movie is not None and self.isMovieDeleted == False:
            try:
                self.movie.frameChanged.disconnect()
                self.movie.stop()
                self.imageScene.removeItem(self.pixmap_item)
                self.movie.deleteLater()
                del self.movie
                del self.pixmap_item
                self.isMovieDeleted = True
            except TypeError as e:
                print(f"Exception when disconnecting movie: {e}")
        if hasattr(self, 'media_player') and self.media_player is not None and self.isMediaPlayerDeleted == False:
            try:
                #self.media_player.setSource(QUrl())
                self.media_player.mediaStatusChanged.disconnect()
                self.media_player.stop()
                self.imageScene.removeItem(self.video_item)
                self.media_player.deleteLater()
                self.video_item.deleteLater()
                self.isMediaPlayerDeleted = True
                #del self.media_player
                #del self.video_item
            except Exception as e:
                print(f"Exception when disconnecting media player: {e}")
        self.imageScene.clear()

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if Path(file_path).is_dir() or Path(file_path).suffix.lower() in ['.png', '.gif', '.webp', '.mp4']:
                        # accept local files
                        event.acceptProposedAction()
                        return
                elif url.scheme() in ('http', 'https'):
                    # accept image links
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            new_files = []
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if Path(file_path).is_dir():
                        new_files.extend(self.fileHandler.getFilesFromFolder(file_path))
                    elif 'Temp' in Path(file_path).parts:
                        copied_path = self.fileHandler.copyTempImage(file_path)
                        new_files.append(copied_path)
                    elif not self.fileHandler.isFileInList(file_path):
                        new_files.append(file_path)
                elif url.scheme() == 'http' or url.scheme() == 'https':
                    downloaded_path = self.fileHandler.downloadImage(url)
                    if downloaded_path and not self.fileHandler.isFileInList(downloaded_path):
                        new_files.append(downloaded_path)

        self.fileHandler.updateFileList(new_files)
        event.acceptProposedAction()

    def handleItemSelectionChanged(self):
        selectedItem = self.fileList.currentItem()
        if selectedItem:
            self.viewMetadata(selectedItem)
            #if 0 <= selectedIndex < len(self.selectedFiles):
                #self.viewMetadata(selectedItem)

    def updateImageView(self):
        self.imageView.fitInView(self.imageScene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.imageView.resetZoom()

    def updateVideoView(self):
        self.imageView.resetTransform()
        self.imageScene.setSceneRect(self.video_item.boundingRect())
        self.imageView.setScene(self.imageScene)
        self.imageView.fitInView(self.imageScene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.imageView.resetZoom()

    def saveSettings(self):
        file_paths = self.fileHandler.getFileList()
        self.settings.setValue("selectedFiles", file_paths)
        self.settings.setValue("main_window_state", self.saveState())
        self.settings.setValue("main_window_geometry", self.saveGeometry())

    def loadSettings(self):
        file_paths = self.settings.value("selectedFiles", [])
        self.fileHandler.updateFileList(file_paths)
        
        if self.settings.value("main_window_state"):
            self.restoreState(self.settings.value("main_window_state"))
        
        if self.settings.value("main_window_geometry"):
            self.restoreGeometry(self.settings.value("main_window_geometry"))
        else:
            self.resize(720,720)

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()
    
    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Type.Resize:
                self.updateImageView()
        if obj in (self.fileListWidget, self.imageViewWidget):
            if event.type() == QEvent.Type.Move:
                self.updateImageView()
        if obj == self.fileList:
            if event.type() == QEvent.Type.Resize and self.initialized == True:
                self.fileHandler.lazyLoadIcon()
        return super(MainWindow, self).eventFilter(obj, event)

    def showContextMenu(self, event):
        menu = QMenu(self)
        view_action = QAction("View", self)
        view_action.triggered.connect(self.openImage)
        openfolder_action = QAction("Open folder", self)
        openfolder_action.triggered.connect(self.openFolder)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.fileHandler.removeSelectedItem)
        test_action = QAction("Test", self)
        test_action.triggered.connect(self.test)
        menu.addAction(view_action)
        menu.addAction(openfolder_action)
        menu.addAction(remove_action)
        menu.addAction(test_action)
        menu.exec(self.fileList.mapToGlobal(event))

    def test(self):
        '''rect = self.fileList.viewport().contentsRect()
        for row in range(self.fileList.count()):
            index = self.fileList.model().index(row, 0)
            item = self.fileList.itemFromIndex(index)

            if item and self.isItemVisible(item, rect):
                print(f"Filename: {item.data(0)}")'''

        self.fileHandler.lazyLoadIcon()

    def isItemVisible(self, item, rect):
        item_rect = self.fileList.visualItemRect(item)
        return item_rect.intersects(rect)
            
    def openFolder(self):
        selectedItem = self.fileList.currentItem()
        if selectedItem:
            selectedFile = selectedItem.text()
            folder_path = Path(selectedFile).parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
    
    def openImage(self):
        selectedItem = self.fileList.currentItem()
        if selectedItem:
            selectedFile = selectedItem.text()
            subprocess.run(['start', '', selectedFile], shell=True)

    def showAboutDialog(self):
        self.setEnabled(False)
        about_dialog = AboutDialog(self)
        about_dialog.setModal(True)
        about_dialog.show()

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
    if shared_memory.attach():
        is_running = True
    else:
        shared_memory.create(1)
        is_running = False

    semaphore.release()

    if is_running:
        QMessageBox.warning(None, 'Application already running', 'One instance of the application is already running.')
        return
    
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    iconPath = resource_path("icon/icon.ico")
    app.setWindowIcon(QIcon(iconPath))
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    launch()