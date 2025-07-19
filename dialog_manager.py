import os
import platform
import subprocess
import tempfile
from PyQt5.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QPushButton, QDialog, QHBoxLayout, QLabel, QWidget, QTextEdit
from PyQt5.QtGui import QColor, QPalette, QFont, QFontDatabase, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QPoint, QRectF, QTimer
from utils import log

class DialogManager:
    def __init__(self, tails_state_machine=None, gemini_manager=None):
        self.tails_state_machine = tails_state_machine
        self.active_speech_bubble = None
        self.gemini_manager = gemini_manager

        self.speech_bubble_follow_timer = QTimer()
        self.speech_bubble_follow_timer.timeout.connect(self.update_speech_bubble)

    def _get_tails_position(self):
        if self.tails_state_machine:
            state = self.tails_state_machine.get_state()
            return state["position"]
        return None, None

    def _create_temporary_parent(self, parent_x, parent_y):
        if parent_x is not None and parent_y is not None:
            temp_parent = QWidget()
            temp_parent.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            temp_parent.setAttribute(Qt.WA_TranslucentBackground)
            temp_parent.setFixedSize(1, 1)
            temp_parent.move(parent_x, parent_y)
            temp_parent.show()
            return temp_parent
        return None

    def get_option(self, title="Select Option", options=None):
        # Initalize Window Config
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 150)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        selected_option = None

        # Layout
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel(title)

        # Font
        font_id = QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "NationalPark-SemiBold.ttf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        title_label.setFont(QFont(font_family, 14, 600))

        # Styles
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #876156;")
        main_layout.addWidget(title_label)

        # Option Layout
        options_layout = QHBoxLayout()
        options_layout.setSpacing(10)
        options_layout.setAlignment(Qt.AlignCenter)

        if options is None:
            options = ["Option 1", "Option 2", "Option 3"]

        def on_button_clicked(option_text):
            nonlocal selected_option
            selected_option = option_text
            dialog.accept()

        for option_text in options:
            # Button Styles and Config
            button = QPushButton(option_text)
            button.setFont(QFont(font_family, 10, QFont.Medium))
            button.setStyleSheet(
                "QPushButton {"
                "  background-color: #876156;"
                "  color: white;"
                "  border-radius: 10px;"
                "  padding: 10px 20px;"
                "  border: none;"
                "}"
                "QPushButton:hover {"
                "  background-color: #6a4c42;"
                "}"
                "QPushButton:pressed {"
                "  background-color: #553e36;"
                "}"
            )
            button.clicked.connect(lambda checked, text=option_text: on_button_clicked(text))
            options_layout.addWidget(button)

        main_layout.addLayout(options_layout)

        # Dialog Styles
        dialog.setStyleSheet(
            "QDialog {"
            "  background-color: #e6ccb1;"
            "  border: 2px solid #876156;"
            "  border-radius: 10px;"
            "}"
        )

        # Position
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        dialog.move(
            (screen_geometry.width() - dialog.width()) // 2,
            (screen_geometry.height() - dialog.height()) // 2,
        )

        result = None
        if dialog.exec_() == QDialog.Accepted:
            result = selected_option

        return result

    def get_user_input(self, title="Input", placeholder_text="Enter text here...", is_password=False):
        # Setup active coords
        tails_x, tails_y = self._get_tails_position()
        dummy_parent = self._create_temporary_parent(tails_x, tails_y)
        dialog = QDialog(dummy_parent if dummy_parent else None)

        # Window Config
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 100)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        dialog.setAttribute(Qt.WA_TranslucentBackground)

        # Something idk
        palette = dialog.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        dialog.setPalette(palette)
        dialog.setAutoFillBackground(True)

        input_field = QLineEdit(dialog)

        # Fonts
        font_id = QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "NationalPark-SemiBold.ttf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        input_field.setFont(QFont(font_family, 12))

        input_field.setStyleSheet(
            "QLineEdit {"
            "  color: #876156;"
            "  background-color: #e6ccb1;"
            "  border: 2px solid #876156;"
            "  border-radius: 5px;"
            "  padding: 5px;"
            "}"
        )
        input_field.setAlignment(Qt.AlignCenter)
        input_field.setPlaceholderText(placeholder_text)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)

        set_button = QPushButton("Submit", dialog)
        set_button.setFont(QFont(font_family))

        set_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #876156;"
            "  color: white;"
            "  border-radius: 5px;"
            "  padding: 8px 15px;"
            "  margin-left: 5px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #6a4c42;"
            "}"
        )

        input_value = None

        def button_clicked():
            nonlocal input_value
            input_value = input_field.text().strip()
            dialog.accept()

        set_button.clicked.connect(button_clicked)
        input_field.returnPressed.connect(button_clicked)

        input_layout = QHBoxLayout()
        input_layout.addWidget(input_field)
        input_layout.addWidget(set_button)
        input_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 10, 20, 10)

        dialog.setLayout(main_layout)

        if dummy_parent:
            dialog.move(tails_x - dialog.width() // 2, tails_y - dialog.height() - 120)
        else:
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            dialog.move(
                (screen_geometry.width() - dialog.width()) // 2,
                (screen_geometry.height() - dialog.height()) // 2,
            )

        result = None
        if dialog.exec_() == QDialog.Accepted:
            result = input_value

        if dummy_parent:
            dummy_parent.close()
            dummy_parent.deleteLater()

        return result

    def _hide_speech_bubble(self):
        if self.active_speech_bubble:
            self.speech_bubble_follow_timer.stop()
            self.active_speech_bubble.hide()
            log("Speech bubble hidden.", level="INFO")

    def show_speech_bubble(self, text, bubble_width=300, bubble_height=100):
        self._hide_speech_bubble()

        tails_x, tails_y = self._get_tails_position()
        bubble_dialog = QDialog()
        bubble_dialog.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        bubble_dialog.setAttribute(Qt.WA_TranslucentBackground)
        bubble_dialog.setFixedSize(bubble_width, bubble_height)

        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        text_edit.setFocusPolicy(Qt.NoFocus)

        text_edit.setStyleSheet("""
            QTextEdit {
                color: #876156;
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: 1px solid #999;
                background: #e6ccb1;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #876156;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: 1px solid #999;
                background: #e6ccb1;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #876156;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: none;
            }
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        font_id = QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "NationalPark-SemiBold.ttf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        text_edit.setFont(QFont(font_family, 10))

        main_layout = QVBoxLayout(bubble_dialog)
        main_layout.setContentsMargins(15, 15, 15, 25)
        main_layout.addWidget(text_edit)

        def paint_bubble_event(event):
            painter = QPainter(bubble_dialog)
            painter.setRenderHint(QPainter.Antialiasing)

            bubble_color = QColor("#e6ccb1")
            border_color = QColor("#876156")
            border_radius = 10

            bubble_body_rect = bubble_dialog.rect().adjusted(0, 0, 0, -20)
            path = QPainterPath()
            path.addRoundedRect(QRectF(bubble_body_rect), border_radius, border_radius)

            tail_height = 20
            tail_width = 30
            tail_base_left = QPoint(bubble_dialog.width() // 2 - tail_width // 2, bubble_body_rect.bottom())
            tail_base_right = QPoint(bubble_dialog.width() // 2 + tail_width // 2, bubble_body_rect.bottom())
            tail_tip = QPoint(bubble_dialog.width() // 2, bubble_dialog.height() - 2)
            control_point_offset_y = 5
            control_point = QPoint(bubble_dialog.width() // 2, bubble_body_rect.bottom() + tail_height - control_point_offset_y)

            path.moveTo(tail_base_left)
            path.quadTo(control_point, tail_tip)
            path.quadTo(control_point, tail_base_right)

            painter.setBrush(bubble_color)
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

            painter.setPen(QColor(border_color))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

        bubble_dialog.paintEvent = paint_bubble_event

        if tails_x is not None and tails_y is not None:
            offset_x = 0
            offset_y = -bubble_dialog.height() - 10

            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()

            target_x = tails_x + offset_x - (bubble_dialog.width() // 2)
            target_y = tails_y + offset_y

            target_x = max(
                screen_geometry.left(), min(target_x + 200, screen_geometry.right() - bubble_dialog.width())
            )
            target_y = max(
                screen_geometry.top(), min(target_y + 35, screen_geometry.bottom() - bubble_dialog.height())
            )

            bubble_dialog.move(target_x, target_y)
        else:
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            bubble_dialog.move(
                (screen_geometry.width() - bubble_dialog.width()) // 2,
                (screen_geometry.height() - bubble_dialog.height()) // 2,
            )

        self.active_speech_bubble = bubble_dialog
        bubble_dialog.show()

        # Removed the hide timer start
        # Start the follow timer (e.g., update every 50ms for smooth movement)
        self.speech_bubble_follow_timer.start(50)

    def update_speech_bubble(self):
        if self.active_speech_bubble:
            tails_x, tails_y = self._get_tails_position()
            if tails_x is not None and tails_y is not None:
                offset_x = 0
                offset_y = -self.active_speech_bubble.height() - 10

                screen = QApplication.primaryScreen()
                screen_geometry = screen.availableGeometry()

                target_x = tails_x + offset_x - (self.active_speech_bubble.width() // 2)
                target_y = tails_y + offset_y

                target_x = max(
                    screen_geometry.left(), min(target_x + 200, screen_geometry.right() - self.active_speech_bubble.width())
                )
                target_y = max(
                    screen_geometry.top(), min(target_y + 35, screen_geometry.bottom() - self.active_speech_bubble.height())
                )
                self.active_speech_bubble.move(target_x, target_y)

    # Here because it needs to run on the GUI thread
    def _handle_code(self, code):
        selected_option = self.get_option(
            title="Code Options",
            options=["Implement Code", "Open in Notepad", "Cancel"]
        )

        if selected_option == "Implement Code":
            file_path = self.get_user_input(title="Save Code to File", placeholder_text="Enter file path (e.g., my_script.py)")
            if file_path:
                dir_name = os.path.dirname(file_path)
                if dir_name and not os.path.exists(dir_name):
                    os.makedirs(dir_name, exist_ok=True)
                    log(f"Created directory: {dir_name}", level="INFO")

                file_content = ""
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()
                        log(f"Read existing file content from {file_path}", level="INFO")
                    except Exception as e:
                        log(f"Error reading existing file {file_path}: {e}", level="ERROR")
                        file_content = ""

                if self.gemini_manager and self.gemini_manager.client and self.gemini_manager.api_key_set_successfully:
                    gemini_prompt = f"""
                    You are an expert code assistant. Here is the current content of the file:
                    ---FILE START---\n{file_content}\n---FILE END---

                    Here is the code to implement:
                    ---CODE START---\n{code}\n---CODE END---

                    Please update the file content by implementing the new code as needed, merging or integrating it in the most logical way. Only return the full updated file content, nothing else.
                    """
                    try:
                        response = self.gemini_manager.client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=gemini_prompt
                        )
                        new_content = self.gemini_manager._extract_code(response.text.strip())
                        if new_content:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            log(f"File {file_path} updated by Tails.", level="INFO")
                        else:
                            log("Tails couldn't generate merged code. Writing original code to file.", level="WARNING")
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(code)
                    except Exception as e:
                        log(f"Failed to merge code with Gemini model: {e}. Writing original code to file instead.", level="ERROR")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(code)
                else:
                    log("Gemini client not initialized or API key not set. Cannot merge code. Writing original code to file.", level="WARNING")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(code)
            else:
                log("File path input cancelled.", level="INFO")

        elif selected_option == "Open in Notepad":
            log("Opening code in notepad...", level="INFO")
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                    tmp.write(code)
                    tmp_path = tmp.name
                if platform.system() == "Windows":
                    subprocess.Popen(["notepad.exe", tmp_path])
                else:
                    editor = os.environ.get("EDITOR", "nano")
                    subprocess.Popen([editor, tmp_path])
                log(f"Code opened in temporary file: {tmp_path}", level="INFO")
            except Exception as e:
                log(f"Failed to open code in editor: {e}", level="ERROR")
        else:
            log("Code handling cancelled.", level="INFO")