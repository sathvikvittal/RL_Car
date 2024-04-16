import socketio
import eventlet
import numpy as np
from flask import Flask
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import cv2

sio_server = socketio.Server()

app = Flask(__name__)

MAX_SPEED = 20

def img_preprocess(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img

@sio_server.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/MAX_SPEED
    print('{} {} {}'.format(steering_angle, throttle, speed))
    control_send(steering_angle, throttle)

    
@sio_server.on('connect')
def connect(sid,env):
    print("------------------------ Connected ------------------------")
    control_send(0,0)

def control_send(angle,throttle):
    sio_server.emit('steer', data={
        'steering_angle' : angle.__str__(),
        'throttle' : throttle.__str__()
    })


if __name__ == '__main__':
    model = load_model('model.h5')
    app = socketio.Middleware(sio_server, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)