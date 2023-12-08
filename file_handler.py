import os, requests, shutil
from pathlib import Path
from urllib.parse import unquote
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, QRunnable, QThreadPool
from collections import OrderedDict

class FileHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.thumbnailCache = OrderedDict()
        self.maxCacheSize = 20
    
    def downloadImage(self, url):
        try:
            response = requests.get(url.toString())
            if response.status_code == 200:
                # get the file extension from the content-type header
                url_filename = os.path.basename(unquote(url.toString()))
                invalid_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
                for char in invalid_characters:
                    url_filename = url_filename.replace(char, '_')
                file_extension = response.headers.get('Content-Type').split('/')[-1]
                # create a unique filename in the current working directory
                filename = f"{url_filename}.{file_extension}"
                save_path = os.path.join(os.getcwd(), f"{url_filename}.{file_extension}")
                # save the image locally
                with open(filename, 'wb') as file:
                    file.write(response.content)
                return save_path
            else:
                print(f"Failed to download image. HTTP Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading image: {e}")
        return None
    
    def copyTempImage(self, temp_file_path):
        try:
            # create a copy of the image file in the current working directory
            copied_path = os.path.join(os.getcwd(), os.path.basename(temp_file_path))
            shutil.copyfile(temp_file_path, copied_path)
            return copied_path
        except Exception as e:
            print(f"Error copying temp image: {e}")
            return None
        
    def openFileDialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            "Select image files",
            "",
            "Images and videos (*.png *.jpg *.gif *.webp *.mp4)"
        )
        if filenames:
            self.updateFileList(filenames)
    
    def updateFileList(self, file_paths):
        for file_path in file_paths:
            item = QListWidgetItem()
            #item.setSizeHint(QSize(200, 200)) 
            #loader = ImageLoader(file_path, item)
            #threadPool.start(loader)
            #threadPool.waitForDone()
            filename = os.path.basename(file_path)
            item.setData(0, filename)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.main_window.fileList.addItem(item)
        self.main_window.fileList.setIconSize(QSize(100,100))
        if self.main_window.fileList.count() > 0:
            last_item = self.main_window.fileList.item(self.main_window.fileList.count() - 1)
            self.main_window.fileList.setCurrentItem(last_item)
            self.main_window.viewMetadata(last_item)
        else:
            self.main_window.viewMetadata(None)

    def lazyLoadIcon(self):
        threadPool = QThreadPool.globalInstance()
        rect = self.main_window.fileList.viewport().contentsRect()
        for row in range(self.main_window.fileList.count()):
            index = self.main_window.fileList.model().index(row, 0)
            item = self.main_window.fileList.itemFromIndex(index)

            if item and self.isItemVisible(item, rect):
                if item.data(Qt.ItemDataRole.DecorationRole) is None:
                    filePath = item.data(Qt.ItemDataRole.UserRole)
                    loader = ImageLoader(self.main_window, filePath, item, self.thumbnailCache, index, self.maxCacheSize)
                    threadPool.start(loader)
    
    def isItemVisible(self, item, rect):
        item_rect = self.main_window.fileList.visualItemRect(item)
        return item_rect.intersects(rect)

    def clearFileList(self):
        self.main_window.fileList.clear()
        #self.main_window.imageScene.clear()
        self.main_window.selectedFile.clear()
        for _, widget, _ in self.main_window.widgetInfo:
            widget.clear()
        self.main_window.viewMetadata(None)

    def removeSelectedItem(self):
        selectedItem = self.main_window.fileList.currentItem()
        if selectedItem:
            selectedIndex = self.main_window.fileList.row(selectedItem)
            self.main_window.fileList.takeItem(selectedIndex)
            # if last index
            if selectedIndex == (self.main_window.fileList.count()):
                if self.main_window.fileList.count() > 0:
                    last_item = self.main_window.fileList.item(self.main_window.fileList.count() - 1)
                    self.main_window.fileList.setCurrentItem(last_item)
                    self.main_window.viewMetadata(last_item)
                else:
                    self.main_window.viewMetadata(None)
            else:
                self.main_window.viewMetadata(self.main_window.fileList.item(selectedIndex))

    def getFilesFromFolder(self, path):
        folder_path = Path(path)
        png_files = list(folder_path.rglob('*.[pP][nN][gG]'))
        jpg_files = list(folder_path.rglob('*.[jJ][pP][gG]'))
        webp_files = list(folder_path.rglob('*.[wW][eE][bB][pP]'))
        gif_files = list(folder_path.rglob('*.[gG][iI][fF]'))
        mp4_files = list(folder_path.rglob('*.[mM][pP][4]'))
        png_files = [str(file_path).replace('\\', '/') for file_path in png_files]
        jpg_files = [str(file_path).replace('\\', '/') for file_path in jpg_files]
        webp_files = [str(file_path).replace('\\', '/') for file_path in webp_files]
        gif_files = [str(file_path).replace('\\', '/') for file_path in gif_files]
        mp4_files = [str(file_path).replace('\\', '/') for file_path in mp4_files]
        image_files = set(png_files + jpg_files + webp_files + gif_files + mp4_files)
        unique_image_files = image_files

        return unique_image_files

    def isFileInList(self, file_path):
        for row in range(self.main_window.fileList.count()):
            item = self.main_window.fileList.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                return True
        return False

    def getFileList(self):
        return [self.main_window.fileList.item(row).data(Qt.ItemDataRole.UserRole) for row in range(self.main_window.fileList.count())]
    
    def getCacheSize(self):
        return len(self.thumbnailCache)

class ImageLoader(QRunnable):
    def __init__(self, main_window, file_path, item, thumbnailCache, index, maxCacheSize):
        super().__init__()
        self.main_window = main_window
        self.file_path = file_path
        self.item = item
        self.thumbnailCache = thumbnailCache
        self.index = index
        self.maxCacheSize = maxCacheSize

    def run(self):
        thumbnail_pixmap = QPixmap(self.file_path).scaled(100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
        icon = QIcon(thumbnail_pixmap)
        self.thumbnailCache[self.file_path] = self.index #cache + 1
        if len(self.thumbnailCache) > self.maxCacheSize:
            rect = self.main_window.fileList.viewport().contentsRect()
            (key, index) = self.popUnusedItem(rect)
            item = self.main_window.fileList.itemFromIndex(index)
            item.setData(1, None)
        self.item.setData(1, icon)

    def popUnusedItem(self, rect):
        key, index = self.thumbnailCache.popitem(last=None)
        item = self.main_window.fileList.itemFromIndex(index)
        if self.isItemVisible(item, rect):
            self.thumbnailCache[key] = index
            return self.popUnusedItem(rect)
        else:
            return key, index
        
    def isItemVisible(self, item, rect):
        item_rect = self.main_window.fileList.visualItemRect(item)
        return item_rect.intersects(rect)