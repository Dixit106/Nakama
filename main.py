import sys 
from PyQt6.QtWidgets import QApplication, QWidget, QLabel 
from PyQt6.QtGui import QPixmap 
from PyQt6.QtCore import Qt, QPoint, QTimer

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
        self.sprite_label = QLabel("Nakama", self)
        self.sprite_label.setGeometry(0,0,200,200)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #loading and scaleing pixel-art i made
        self.frames = self.load_frames([
            "assets/pixel_girl_02.png",
            "assets/pixel_girl_01.png"
        ])
        self.current_frame = 0
        self.sprite_label.setPixmap(self.frames[self.current_frame])

        #loop for change 
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.next_frame)
        self.anim_timer.start(600)

    def load_frames(self, paths):
        loaded = []
        for path in paths:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"Warning: Could not load {path}")
            else:
                pixmap = pixmap.scaled(
                    200, 200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation
                )
            loaded.append(pixmap)
        return loaded

    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.sprite_label.setPixmap(self.frames[self.current_frame])

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