from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.logger import Logger

# based on websocket-client==0.40.0
# patch fixes android error : no handlers could be found for logger "websocket"
# changed logger to kivy.logger.Logger
import pickle
import struct
import websocket

#import pyaudio
from audiostream import get_output, AudioSample
# standard libraries (python 2.7)
from threading import *
import time
#p = pyaudio.PyAudio()
CHUNK = 1024
Recordframes = []
stream = get_output(channels=1, buffersize=CHUNK, rate=44100)
sample = AudioSample()
stream.add_sample(sample)
sample.play()
data = b""
payload_size = struct.calcsize("Q")
kv = '''
<WS>:
    orientation: 'vertical'
    the_btn: the_btn
    Button:
        id: the_btn
        text: "Open Websocket"
        on_press: self.parent.pressed_the_btn()
'''
Builder.load_string(kv)


class KivyWebSocket(websocket.WebSocketApp):

    def __init__(self, *args, **kwargs):
        super(KivyWebSocket, self).__init__(*args, **kwargs)
        self.logger = Logger
        self.logger.info('WebSocket: logger initialized')


class WS(BoxLayout):
    the_btn = ObjectProperty()
    pressed = False

    def __init__(self, **kwargs):
        super(WS, self).__init__(**kwargs)
        Logger.info('Layout: initialized')

    def pressed_the_btn(self):
        if self.pressed is False:
            self.pressed = True
            self.the_btn.text = 'connecting to web socket'
            app = App.get_running_app()
            Clock.schedule_once(app.ws_connection)


class WebSocketTest(App):
    ws = None
    url = "ws://fluttersocket23.herokuapp.com/"
    btn_txt = StringProperty('press me')
    layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(WebSocketTest, self).__init__(**kwargs)
        socket_server="ws://fluttersocket23.herokuapp.com/"
        ws = KivyWebSocket(socket_server,
                           on_message=self.on_ws_message,
                           on_error=self.on_ws_error,
                           on_open=self.on_ws_open,
                           on_close=self.on_ws_close,)
        self.ws = ws
        self.logger = Logger
        self.logger.info('App: initiallzed')

    def build(self):
        self.layout = WS()
        return self.layout

    def on_ws_message(self, ws, message):
        self.layout.the_btn.text = 'new data'
        self.logger.info('WebSocket: {}'.format(message))
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
        sample.write(frame)
        return
    def on_ws_error(self, ws, error):
        self.logger.info('WebSocket: [ERROR]  {}'.format(error))

    def ws_connection(self, dt, **kwargs):
        # start a new thread connected to the web socket
        t = Thread(target=self.ws.run_forever)
        t.start()
       # thread.start_new_thread(self.ws.run_forever, ())

    def on_ws_open(self, ws):
        print('connected')
        self.layout.the_btn.text = 'connected'
        # def run(*args):
        #     for i in range(1, 13):
        #         time.sleep(1)
        #         ws.send('Hello %d' % i)
        #     time.sleep(10)
        #     ws.close()
        # # thread.start_new_thread(run, ())
        # t = Thread(target=run)
        # t.start()

    def on_ws_close(self, ws):
        self.layout.the_btn.text = '### closed ###'


if __name__ == "__main__":
    WebSocketTest().run()
