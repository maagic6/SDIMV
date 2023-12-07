from PyQt6.QtWidgets import QDockWidget, QLineEdit, QTextEdit, QGraphicsView, QListWidget, QStyledItemDelegate, QListWidgetItem
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QWheelEvent, QFont, QColor
from qframelesswindow import StandardTitleBar

class CustomDockWidget(QDockWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.main_window = main_window

    def dragEnterEvent(self, event):
        self.main_window.dragEnterEvent(event)

    def dropEvent(self, event):
        self.main_window.dropEvent(event)

class CustomLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            self.focusNextPrevChild(True)
        else:
            super().keyPressEvent(event)

class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document().contentsChanged.connect(self.adjustSize)

    def adjustSize(self):
        document_height = self.document().size().height()
        current_height = self.height()
        if document_height != current_height:
            self.setFixedHeight(int(document_height) + 10 if document_height < 150 else 150)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.adjustSize()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            event.ignore()
        else:
            super().keyPressEvent(event)

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(ZoomableGraphicsView, self).__init__(parent)
        self.current_zoom = 1.0
        self.minimum_zoom = 0.1
        self.maximum_zoom = 25.0

    def wheelEvent(self, event: QWheelEvent):
        event.accept()
        factor = 1.2 if event.angleDelta().y() > 0 else 1.0 / 1.2
        new_zoom = self.current_zoom * factor
        new_zoom = max(self.minimum_zoom, min(self.maximum_zoom, new_zoom))
        scale_factor = new_zoom / self.current_zoom
        self.current_zoom = new_zoom
        self.scale(scale_factor, scale_factor)
    
    def resetZoom(self):
        self.current_zoom = 1.0

class CustomListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setSelectionRectVisible(True)
    def wheelEvent(self, event: QWheelEvent):
        current_index = self.currentRow()
        total_items = self.count()
        if total_items == 0:
            return
        new_index = (current_index - 1) % total_items if event.angleDelta().y() > 0 else (current_index + 1) % total_items
        self.setCurrentRow(new_index)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        try:
            self.updateSpacing()
        except Exception as e:
            print(f"Exception: {e}")

    def updateSpacing(self):
        viewport_width = self.viewport().width()
        num_columns = max(1, viewport_width // 150)

        if num_columns > 1:
            spacing = (viewport_width - (num_columns * 150)) // (num_columns+1)
            #print(f"viewport width:{viewport_width}")
            #print(f"spacing:{spacing}")
            #print(f"column no.:{num_columns}")
            try:
                self.setStyleSheet(f"QListWidget::item {{ margin-left: {spacing}px; width: 145px; height: 145px; border: 0px solid; }}")
            except Exception as e:
                print(f"Exception: {e}")
        else:
            self.setStyleSheet("QListWidget::item { margin-left: 0px; width: 145px; height: 145px; border: 0px solid; }")
    
class CustomTitleBar(StandardTitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        font=QFont("Segoe UI", 10)
        self.minBtn.setHoverColor(Qt.GlobalColor.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.GlobalColor.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.minBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.maxBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.closeBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet("""
            QFont {
                font: Segoe UI,
                font_size: 10
            }
        """)