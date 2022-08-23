from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import pickle
import struct
from threading import *
import pyaudio
import websocket

p = pyaudio.PyAudio()
CHUNK = 1024
Recordframes = []
stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)
data = b""
payload_size = struct.calcsize("Q")
connectState = "Playing"

def on_message(ws, message):
    global data

    while len(data) < payload_size:

        packet = message  # 4K
        # print(type(packet))
        # print(type(data))
        # packet = de.encode('utf-8')
        if not packet: break
        data += packet
    packed_msg_size = data[:payload_size]
    # print('packed_msg_size')
    # print(packed_msg_size)
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    # print('msg_size')
    # print(msg_size)
    while len(data) < msg_size:
        data += message
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    Recordframes.append(frame)
    # _VARS['window'].FindElement('-PROG-').Update("listening")
    stream.write(frame)
    return


def on_error(ws, error):
    global connectState
    connectState = error
    print(error)
    return


def on_close(ws, d, de):
    global connectState
    connectState = 'closed'
    print("### closed ###")
    t = Thread(target=connection)
    t.start()
    return


def on_open(ws):
    global connectState
    connectState = 'opened'
    print("opened")
    # MainApp().update_txt('opended');
    # global data
    # ws.send("hi")
    # ws.send("test")

    return
def connection():
    print('starting')
    ws = websocket.WebSocketApp("wss://fluttersocket23.herokuapp.com/", on_open=on_open, on_message=on_message,
                                on_error=on_error, on_close=on_close)
    # ws.on_open = on_open

    ws.run_forever()
    return
class MainApp(App):
    def build(self):
        self.operators = ["/", "*", "+", "-"]
        self.last_was_operator = None
        self.last_button = None
        main_layout = BoxLayout(orientation="vertical")
        self.solution = TextInput(
            multiline=False, readonly=True, halign="right", font_size=55
        )
        main_layout.add_widget(self.solution)
        # buttons = [
        #     ["7", "8", "9", "/"],
        #     ["4", "5", "6", "*"],
        #     ["1", "2", "3", "-"],
        #     [".", "0", "C", "+"],
        # ]
        # for row in buttons:
        #     h_layout = BoxLayout()
        #     for label in row:
        #         button = Button(
        #             text=label,
        #             pos_hint={"center_x": 0.5, "center_y": 0.5},
        #         )
        #         button.bind(on_press=self.on_button_press)
        #         h_layout.add_widget(button)
        #     main_layout.add_widget(h_layout)

        equals_button = Button(
            text="Start", pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        equals_button.bind(on_press=self.on_solution)
        main_layout.add_widget(equals_button)

        return main_layout

    def on_button_press(self, instance):
        print(1)

        # current = self.solution.text
        # button_text = instance.text
        #
        # if button_text == "C":
        #     # Clear the solution widget
        #     self.solution.text = ""
        # else:
        #     if current and (
        #         self.last_was_operator and button_text in self.operators):
        #         # Don't add two operators right after each other
        #         return
        #     elif current == "" and button_text in self.operators:
        #         # First character cannot be an operator
        #         return
        #     else:
        #         new_text = current + button_text
        #         self.solution.text = new_text
        # self.last_button = button_text
        # self.last_was_operator = self.last_button in self.operators

    def on_solution(self, instance):
        self.solution.text = 'Connected'
        connection()
        # text = self.solution.text
        # if text:
        #     solution = str(eval(self.solution.text))
        #     self.solution.text = solution

    def update_txt(self, str):
        print('hey')
        print(str)
        # self.my = 'kkkk'
        # MainApp.solution.text = str


if __name__ == "__main__":
    app = MainApp()
    app.run()