import sys
import os
import re
import platform
import subprocess
import webbrowser
from google import genai
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from utils import log
from dialog_manager import DialogManager
import threading

class GeminiManager(QObject):
    show_speech_bubble_signal = pyqtSignal(str, int, int, int)
    hide_speech_bubble_signal = pyqtSignal()
    handle_code_request_signal = pyqtSignal(str)
    set_api_key_signal = pyqtSignal()
    get_user_input_signal = pyqtSignal(str, str, bool)
    option_dialog_signal = pyqtSignal(str, list)

    def __init__(self, tails_state_machine):
        super().__init__()
        self.client = None
        self.api_key_set_successfully = False
        self.tails_state_machine = tails_state_machine
        self.dialog_manager = DialogManager(tails_state_machine=self.tails_state_machine, gemini_manager=self)

        self.show_speech_bubble_signal.connect(self.dialog_manager.show_speech_bubble)
        self.hide_speech_bubble_signal.connect(self.dialog_manager._hide_speech_bubble)
        self.handle_code_request_signal.connect(self.dialog_manager._handle_code)
        self.set_api_key_signal.connect(self.set_api_key)

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

    def set_api_key(self):
        log("Opening GUI for API key input...", level="INFO")
        api_key = self.dialog_manager.get_user_input(
            title="Enter Gemini API Key",
            placeholder_text="Paste your Gemini API Key here...",
            is_password=True
        )

        if api_key:
            os.environ["GEM"] = api_key
            log("API key set for current session (os.environ['GEM']).", level="INFO")
            self._set_key(api_key)
            self._init_LLM(api_key)
        else:
            log("API key input cancelled or empty. Not setting environment variable.", level="INFO")
            self.api_key_set_successfully = False
        
        return self.api_key_set_successfully

    def _extract_code(self, response):
        match = re.search(r"```(?:\w+)?\n(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _generate_response(self, full_prompt, user_input):
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )
                tails_response = response.text.strip()

                log(f"Tails: {tails_response}", level="INFO")
                self.show_speech_bubble_signal.emit(tails_response, 300, 100, 7000)

                code = self._extract_code(tails_response)
                if code:
                    self.handle_code_request_signal.emit(code)

                unsure_phrases = ["i'm not sure", "i don't know", "let me check", "i need to look that up"]
                if any(phrase in tails_response.lower() for phrase in unsure_phrases):
                    log("Tails: Let me search that for you...", level="INFO")
                    webbrowser.open(f"https://www.google.com/search?q={user_input}")
            else:
                log("Gemini client is no longer available. Cannot generate response.", level="ERROR")
                self.show_speech_bubble_signal.emit("My systems are offline, can't chat right now.", 300, 100, 7000)

        except Exception as e:
            error_msg = f"Uh-oh! Something glitched during response generation: {e}"
            log(f"Tails: {error_msg}", level="ERROR")
            self.show_speech_bubble_signal.emit(error_msg, 300, 100, 7000)

    def chat(self):
        env_api_key = os.environ.get("GEM")
        if env_api_key:
            if not self._init_LLM(env_api_key):
                self.set_api_key()
                if not self.api_key_set_successfully:
                    log("API Key not successfully set. Cannot start chat.", level="WARNING")
                    return
        else:
            self.set_api_key()
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
                # Show initial greeting bubble, which will auto-hide
                self.show_speech_bubble_signal.emit(greeting, 300, 100, 7000)
            else:
                log("Gemini client is not available. Cannot start chat.", level="ERROR")
                return
        except Exception as e:
            error_msg = f"Uh-oh! I couldn't boot up correctly: {e}"
            log(f"Tails: {error_msg}", level="ERROR")
            self.show_speech_bubble_signal.emit(error_msg, 300, 100, 7000)
            return

        while True:
            try:
                user_input = self.dialog_manager.get_user_input(title="Your Turn", placeholder_text="Type your message here...")

                if user_input is None:
                    log("User cancelled chat input. Exiting chat loop.", level="INFO")
                    farewell = "See ya next time!"
                    log(f"Tails: {farewell}", level="INFO")
                    self.show_speech_bubble_signal.emit(farewell, 300, 100)
                    self.hide_speech_bubble_signal.emit()
                    break
                elif user_input.lower() in ["exit", "quit"]:
                    farewell = "bye!"
                    log(f"Tails: {farewell}", level="INFO")
                    self.show_speech_bubble_signal.emit(farewell, 300, 100)
                    self.hide_speech_bubble_signal.emit()
                    break

                log(f"You: {user_input}", level="INFO")
                full_prompt = f"{self.tails_prompt}\nUser: {user_input}\nTails:"

                response_thread = threading.Thread(target=self._generate_response, args=(full_prompt, user_input))
                response_thread.start()

            except KeyboardInterrupt:
                farewell = "\nWhoa! That was fast. See ya next time!"
                log(f"Tails: {farewell}", level="INFO")
                self.show_speech_bubble_signal.emit(farewell, 300, 100, 7000)
                break
            except Exception as e:
                error_msg = f"Uh-oh! Something glitched: {e}"
                log(f"Tails: {error_msg}", level="ERROR")
                self.show_speech_bubble_signal.emit(error_msg, 300, 100, 7000)
