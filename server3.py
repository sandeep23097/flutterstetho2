import asyncio
import threading, wave, pickle, struct
import websockets

url = "wss://fluttersocket23.herokuapp.com/"

async def audio_stream():

    CHUNK = 1024
    wf = wave.open("lungs_1.wav", 'rb')
    data = None
    payload_size = struct.calcsize("Q")
    print("hhhhhh")
    print(payload_size)
    async with websockets.connect(url) as websocket:

        while True:
            data = wf.readframes(CHUNK)
            a = pickle.dumps(data)
            message = struct.pack("Q", len(a)) + a
            await websocket.send(message)


t1 = threading.Thread(target=asyncio.run(audio_stream()), args=())
t1.start()