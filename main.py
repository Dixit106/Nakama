import sys 
from PyQt6.QtWidgets import QApplication, QWidget, QLabel 
from PyQt6.QtCore import Qt, QPoint

class NakamaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()

        #no titlebar, stay on top & enable transparency
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(200,200)

        #box to see and drag the window
        self.placeholder = QLabel("Nakama", self)
        self.placeholder.setGeometry(0,0,200,200)
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("""
            background-color: rgba(88, 101, 242, 220);
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 24px;
""")

    def mousePressEvent(self, event):
        #to record where we click inside the window
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        #smooth movement of window with drag
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def keyPressEvent(self, event):
        #Esc key to close as there is no title bar or other buttons
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NakamaWindow()
    window.show()
    sys.exit(app.exec())