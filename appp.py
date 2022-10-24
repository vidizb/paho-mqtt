import cv2
import numpy as np
import av
import mediapipe as mp
import streamlit as st
import paho.mqtt.client as mqtt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from cvzone.PoseModule import PoseDetector
import pyglet.media
import threading
import os
import requests
    

detector = PoseDetector()
sound = pyglet.media.load("alarm.wav", streaming=False)
people = False



def process(img):
    img.flags.writeable = False
    img_count = 0
    breakcount = 0
    img = cv2.flip(img, 1)
    img = detector.findPose(img, draw=False)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    img_name = f'image_{img_count}.png'

    soundThread = threading.Thread(target=sound.play, args=())

    if bboxInfo:
        file_bytes = np.asarray(bytearray(fromarray.read()),\
        dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        cv2.rectangle(img, (120, 20), (470, 80), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "PEOPLE DETECTED!!!", (130, 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        breakcount += 1

        url = 'https://api.telegram.org/bot'
        token = "5746323643:AAFtQBs1cIwc4bUWBZVu4u2F4X3vige1TA0"  # Replace Your Token Bot
        chat_id = "739780150"  # Replace Your Chat ID
        caption = "People Detected!!! "
        files = {'photo': open(img_name, 'rb')}
        resp = requests.post(url + token + '/sendPhoto?chat_id=' + chat_id + '&caption=' + caption, files=files)
        print(f'Response Code: {resp.status_code}')

        if breakcount >= 30:
            if people == False:
                img_count += 1
                soundThread.start()
                teleThread.start()
                people = not people
         
    else:
        breakcount = 0
        if people:
            people = not people
    return img


RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class VideoProcessor:
    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")

        image = process(image)

        return av.VideoFrame.from_ndarray(image, format="bgr24")

webrtc_ctx = webrtc_streamer(
    key="WYH",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_processor_factory=VideoProcessor,
    async_processing=True,
)
