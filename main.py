import sys 
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit
from PyQt6.QtGui import QPixmap 
from PyQt6.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal
from brain import ask_brain 
from voice import speak

class BrainWorker(QThread):
    reply_ready = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt 

    def run(self):
        reply = ask_brain(self.prompt)
        self.reply_ready.emit(reply)

class VoiceWorker(QThread):
    started_speaking = pyqtSignal()
    mouth_changed = pyqtSignal(int)

    def __init__(self, text):
        super().__init__()
        self.text = text 

    def run(self):
        speak(
            self.text,
            on_start=self.started_speaking.emit,
            on_mouth=self.mouth_changed.emit
            )

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

        #speech bubble above the sprite
        layout = QVBoxLayout(self)

        #speech bubble
        self.speech_bubble = QLabel("", self)
        self.speech_bubble.setFixedWidth(220)
        self.speech_bubble.setWordWrap(True)
        self.speech_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speech_bubble.setStyleSheet("""
            background-color: rgba(30,30,46,235);
            color: #cdd6f4;
            border: 2px solid #89b4fa;
            border-radius: 12px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: bold;
        """)
        self.speech_bubble.hide()

        #box to see and drag the window
        self.sprite_label = QLabel(self)
        self.sprite_label.setFixedSize(200,200)
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #hidden chatbox (toggls on right click)
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Talk to Magari")
        self.input_box.setStyleSheet("""
            background-color: rgba(30, 30, 46, 240);
            color: #cdd6f4;
            border: 2px solid #89b4fa;
            border-radius: 10px;
            padding: 6px 10px;
            font-size: 12px;
        """)
        input_policy = self.input_box.sizePolicy()
        input_policy.setRetainSizeWhenHidden(True)
        self.input_box.setSizePolicy(input_policy)
        self.input_box.hide()
        self.input_box.returnPressed.connect(self.handle_input)

        layout.addWidget(self.speech_bubble)
        layout.addWidget(self.sprite_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_box)

        #loading and scaleing pixel-art i made
        self.frames = self.load_frames([
            "assets/Magari.png"
        ])
        self.talk_frames = self.load_frames([
                "assets/Magari.png", #closed mouth
                "assets/Magari-02.png", #halfopen mouth
                "assets/Magari-03.png" #fullopen
        ])
        self.is_speaking = False
        self.current_frame = 0
        self.sprite_label.setPixmap(self.frames[self.current_frame])

        #loop for change 
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.next_frame)
        self.anim_timer.start(600)

        #Auto hide timer for speech bubble
        self.bubble_timer = QTimer(self)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.hide_bubble)

        #Test greeting when start
        self.say("Yo! What's Up!")

    def resize_keep_bottom(self):
        bottom_y = self.y() + self.height()
        self.layout().activate()
        self.adjustSize()
        if self.isVisible():
            new_y = max(0, bottom_y - self.height())
            self.move(self.x(), new_y)

    def say(self, text, duration=4000):
        self.speech_bubble.setText(text)
        self.speech_bubble.show()
        self.resize_keep_bottom()
        self.bubble_timer.start(duration)

    def hide_bubble(self):
        self.speech_bubble.hide()
        self.resize_keep_bottom()

    def toggle_input(self):
        if self.input_box.isVisible():
            self.input_box.hide()
        else:
            self.input_box.show()
            self.input_box.setFocus()

    def handle_input(self):
        text = self.input_box.text().strip()
        self.input_box.clear()
        self.input_box.hide()
        if text:
            self.say(f"Thinking...", duration=90000)
            self.worker = BrainWorker(text)
            self.worker.reply_ready.connect(self.on_brain_reply)
            self.worker.start()

    def on_brain_reply(self, reply):
       self.voice_worker = VoiceWorker(reply)
       self.voice_worker.started_speaking.connect(lambda: self.start_speaking(reply))
       self.voice_worker.mouth_changed.connect(self.set_mouth_frame)
       self.voice_worker.finished.connect(self.stop_speaking)
       self.voice_worker.start()

    def start_speaking(self, reply):
        self.is_speaking = True 
        self.say(reply, duration=9000)

    def set_mouth_frame(self, state):
        if self.is_speaking:
            self.sprite_label.setPixmap(self.talk_frames[state])

    def stop_speaking(self):
        self.is_speaking = False 
        self.sprite_label.setPixmap(self.frames[0])

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
        if not self.is_speaking:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.sprite_label.setPixmap(self.frames[self.current_frame])

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.say("Hey! Don't poke me, I will get angery now...")

    def mousePressEvent(self, event):
        #to record where we click inside the window
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.toggle_input()
            event.accept()

    def mouseMoveEvent(self, event):
        #smooth movement of window with drag
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def keyPressEvent(self, event):
        #Esc key to close as there is no title bar or other buttons
        if event.key() == Qt.Key.Key_Escape:
            if self.input_box.isVisible():
                self.input_box.hide()
            else:
                self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NakamaWindow()
    window.show()
    sys.exit(app.exec())