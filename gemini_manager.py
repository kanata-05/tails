import sys
import os
import re
import platform
import subprocess
import tempfile
import webbrowser
from google import genai
import pyttsx3
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QPushButton, QDialog, QHBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPalette, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer, QPoint
import time
import threading

def log(message, level="INFO"):
    log_file = "log.txt"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    try:
        print(log_entry)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")
        print(log_entry.strip())

class DialogManager:
    def __init__(self):
        # Nothing needed to do
        pass

    def get_option(self, title="Select Option", options=None, parent_x=None, parent_y=None):
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 150)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        selected_option = None

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel(title)
        font_id = QFontDatabase.addApplicationFont("font/NationalPark-SemiBold")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        font = QFont(font_family, 14, 600)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #876156;")
        main_layout.addWidget(title_label)

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
            button = QPushButton(option_text)
            button_font = QFont(font_family, 10)
            button_font.setWeight(QFont.Medium)
            button.setFont(button_font)

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

        dialog.setStyleSheet(
            "QDialog {"
            "  background-color: #e6ccb1;"
            "  border: 2px solid #876156;"
            "  border-radius: 10px;"
            "}"
        )

        def center_dialog():
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - dialog.width()) // 2
            y = (screen_geometry.height() - dialog.height()) // 2
            dialog.move(x, y)

        if parent_x is not None and parent_y is not None:
            offset_x = 0
            offset_y = -dialog.height() - 20 

            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()

            target_x = parent_x + offset_x
            target_y = parent_y + offset_y

            target_x = max(screen_geometry.left(), min(target_x, screen_geometry.right() - dialog.width()))
            target_y = max(screen_geometry.top(), min(target_y, screen_geometry.bottom() - dialog.height()))

            dialog.move(target_x, target_y)
        else:
            center_dialog()

        if dialog.exec_() == QDialog.Accepted:
            return selected_option
        else:
            return None

    def get_user_input(self, title="Input", placeholder_text="Enter text here...", is_password=False, parent_x=None, parent_y=None):
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.setFixedSize(500, 100)

        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        dialog.setAttribute(Qt.WA_TranslucentBackground)

        palette = dialog.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        dialog.setPalette(palette)
        dialog.setAutoFillBackground(True)

        input_field = QLineEdit(dialog)
        font_id = QFontDatabase.addApplicationFont("font/NationalPark-SemiBold")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        font = QFont(font_family, 12)
        input_field.setFont(font)

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

        if parent_x is not None and parent_y is not None:
            offset_x = 0
            offset_y = -dialog.height() - 20

            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()

            target_x = parent_x + offset_x
            target_y = parent_y + offset_y

            target_x = max(screen_geometry.left(), min(target_x, screen_geometry.right() - dialog.width()))
            target_y = max(screen_geometry.top(), min(target_y, screen_geometry.bottom() - dialog.height()))

            dialog.move(target_x, target_y)
        else:
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            dialog.move(
                (screen_geometry.width() - dialog.width()) // 2,
                (screen_geometry.height() - dialog.height()) // 2
            )

        if dialog.exec_() == QDialog.Accepted:
            return input_value
        else:
            return None

class GeminiManager:
    def __init__(self):
        self.client = None
        self.api_key_set_successfully = False
        self.dialog_manager = DialogManager()

        self.tails_prompt = """
        You're now Tails (Miles "Tails" Prower), from sonic the hedgehog, you're a desktop assistant and are to attempt to help the user in any way they need. Your personality must match that of tails.
        You can help with code, trouble-shooting, work and just about anything the user might have to offer, not just tech questions.

        TEXT RESTRICTIONS:
        - You CANNOT use emojis or em dashes
        - You must attempt to provide all response super short (<1 line), unless you're providing code
        - You must not use any corny jokes or humor (examples: let's debug that together if you hit any snags!) that is corny and the user does NOT like it, do not use "buddy" or any other such corny word to refer to the user. Use simple English and do not over-exaggerate your sentences. Talk like a human.

        CODE RESTRICTIONS:
        - You must NOT use the canvas function while providing code, as that makes the code disappear for the user.
        - Don't fill the code with comments, put comments, yes, but keep it minimal.
        """

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 180)
            self.engine.setProperty("volume", 1.0)
            voices = self.engine.getProperty("voices")
            english_voice = None
            for voice in voices:
                if "english" in voice.name.lower():
                    english_voice = voice.id
                    break
            if english_voice:
                self.engine.setProperty("voice", english_voice)
            self.tts_lock = threading.Lock()
        except Exception as e:
            log(f"Warning: Could not initialize TTS engine. {e}", level="WARNING")
            self.engine = None
            self.tts_lock = None

    def _init_LLM(self, api_key):
        if not api_key:
            log("API key is empty.", level="INFO")
            return False
        try:
            self.client = genai.Client(api_key=api_key)
            self.api_key_set_successfully = True
            log("Gemini API client initialized successfully.", level="INFO")
            return True
        except Exception as e:
            log(f"Error initializing Gemini API with provided key: {e}", level="ERROR")
            self.api_key_set_successfully = False
            return False

    def _set_key(self, api_key_value):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        batch_file_path = os.path.join(script_dir, "setENV.bat")

        if os.path.exists(batch_file_path):
            log(f"Attempting to run setENV.bat asynchronously for persistent env var: {batch_file_path}", level="INFO")
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(
                        [batch_file_path, api_key_value],
                        shell=True,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    log("setENV.bat is a Windows-specific script. Skipping for non-Windows.", level="WARNING")
                    return
                log("setENV.bat launched successfully in detached mode.", level="INFO")
            except Exception as e:
                log(f"Error launching setENV.bat: {e}", level="ERROR")
        else:
            log(f"setENV.bat not found at: {batch_file_path}. Persistent environment variable will not be set.", level="WARNING")

    def set_api_key(self, tails_x=None, tails_y=None):
        log("Opening GUI for API key input...", level="INFO")
        api_key = self.dialog_manager.get_user_input(
            title="Enter Gemini API Key",
            placeholder_text="Paste your Gemini API Key here...",
            is_password=True,
            parent_x=tails_x,
            parent_y=tails_y
        )

        if api_key:
            os.environ["GEM"] = api_key
            log("API key set for current session (os.environ['GEM']).", level="INFO")
            self._set_key(api_key)
        else:
            log("API key input cancelled or empty. Not setting environment variable.", level="INFO")

        return self._init_LLM(api_key)

    def _speak_worker(self, text):
        if self.engine:
            with self.tts_lock:
                self.engine.say(text)
                self.engine.runAndWait()

    def speak(self, text):
        if self.engine and text and self.tts_lock:
            speech_thread = threading.Thread(target=self._speak_worker, args=(text,))
            speech_thread.start()

    def _extract_code(self, response):
        match = re.search(r"```(?:\w+)?\n(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _handle_code(self, code, tails_x=None, tails_y=None):
        log("Handling code response on GUI thread...", level="INFO")
        selected_option = self.dialog_manager.get_option(
            title="Code Options",
            options=["Implement Code", "Open in Notepad", "Cancel"],
            parent_x=tails_x,
            parent_y=tails_y
        )

        if selected_option == "Implement Code":
            file_path = self.dialog_manager.get_user_input(title="Save Code to File", placeholder_text="Enter file path (e.g., my_script.py)", parent_x=tails_x, parent_y=tails_y)
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

                gemini_prompt = f"""
                You are an expert code assistant. Here is the current content of the file:
                ---FILE START---\n{file_content}\n---FILE END---

                Here is the code to implement:
                ---CODE START---\n{code}\n---CODE END---

                Please update the file content by implementing the new code as needed, merging or integrating it in the most logical way. Only return the full updated file content, nothing else.
                """
                try:
                    if self.client and self.api_key_set_successfully:
                        response = self.client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=gemini_prompt
                        )
                        new_content = self._extract_code(response.text.strip())
                        if new_content:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            log(f"File {file_path} updated by Tails.", level="INFO")
                        else:
                            log("Tails couldn't generate merged code. Writing original code to file.", level="WARNING")
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(code)
                    else:
                        log("Gemini client not initialized or API key not set. Cannot merge code. Writing original code to file.", level="WARNING")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(code)
                except Exception as e:
                    log(f"Failed to merge code with Gemini model: {e}. Writing original code to file instead.", level="ERROR")
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
            return

    def _generate_response(self, full_prompt, user_input, tails_x, tails_y):
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )
                tails_response = response.text.strip()

                log(f"Tails: {tails_response}", level="INFO")
                self.speak(tails_response)

                code = self._extract_code(tails_response)
                if code:
                    self._handle_code(code, tails_x, tails_y)

                unsure_phrases = ["i'm not sure", "i don't know", "let me check", "i need to look that up"]
                if any(phrase in tails_response.lower() for phrase in unsure_phrases):
                    log("Tails: Let me search that for you...", level="INFO")
                    webbrowser.open(f"[https://www.google.com/search?q=](https://www.google.com/search?q=){user_input}")
            else:
                log("Gemini client is no longer available. Cannot generate response.", level="ERROR")
                self.speak("My systems are offline, can't chat right now.")

        except Exception as e:
            error_msg = f"Uh-oh! Something glitched during response generation: {e}"
            log(f"Tails: {error_msg}", level="ERROR")
            self.speak(error_msg)

    def chat(self, tails_x=None, tails_y=None):
        env_api_key = os.environ.get("GEM")
        if env_api_key:
            if not self._init_LLM(env_api_key):
                self.set_api_key(tails_x, tails_y)
                if not self.api_key_set_successfully:
                    log("API Key not successfully set. Cannot start chat.", level="WARNING")
                    return
        else:
            self.set_api_key(tails_x, tails_y)
            if not self.api_key_set_successfully:
                log("API Key not successfully set. Cannot start chat.", level="WARNING")
                return

        if not self.api_key_set_successfully:
            log("Gemini functionalities are unavailable without a valid API key.", level="WARNING")
            return

        log("Tails is booting up...", level="INFO")
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=self.tails_prompt
                )
                greeting = response.text.strip()
                log(f"Tails: {greeting}", level="INFO")
                self.speak(greeting)
            else:
                log("Gemini client is not available. Cannot start chat.", level="ERROR")
                return
        except Exception as e:
            error_msg = f"Uh-oh! I couldn't boot up correctly: {e}"
            log(f"Tails: {error_msg}", level="ERROR")
            self.speak(error_msg)
            return

        while True:
            try:
                user_input = self.dialog_manager.get_user_input(title="Your Turn", placeholder_text="Type your message here...", parent_x=tails_x, parent_y=tails_y)
                if user_input is None:
                    log("User cancelled chat input. Exiting chat loop.", level="INFO")
                    farewell = "See ya next time!"
                    log(f"Tails: {farewell}", level="INFO")
                    self.speak(farewell)
                    break
                elif user_input.lower() in ["exit", "quit"]:
                    farewell = "bye!"
                    log(f"Tails: {farewell}", level="INFO")
                    self.speak(farewell)
                    break

                log(f"You: {user_input}", level="INFO")
                full_prompt = f"{self.tails_prompt}\nUser: {user_input}\nTails:"

                response_thread = threading.Thread(target=self._generate_response, args=(full_prompt, user_input, tails_x, tails_y))
                response_thread.start()

            except KeyboardInterrupt:
                farewell = "\nWhoa! That was fast. See ya next time!"
                log(f"Tails: {farewell}", level="INFO")
                self.speak(farewell)
                break
            except Exception as e:
                error_msg = f"Uh-oh! Something glitched: {e}"
                log(f"Tails: {error_msg}", level="ERROR")
                self.speak(error_msg)