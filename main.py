import cv2
import pyglet.media
from cvzone.FaceDetectionModule import FaceDetector
import av
import csv
from datetime import datetime
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration


detector = FaceDetector()

sound = pyglet.media.load("alarm.wav", streaming=False)

def alert():
    cv2.rectangle(img, (700, 20), (1250, 80), (0, 0, 255), cv2.FILLED)
    cv2.putText(img, "DROWSINESS ALERT!!!", (710, 60),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)

def recordData(condition):
    file = open("database.csv", "a", newline="")
    now = datetime.now()
    dtString = now.strftime("%d-%m-%Y %H:%M:%S")
    tuple = (dtString, condition)
    writer = csv.writer(file)
    writer.writerow(tuple)
    file.close()

def process(img):
    img, bboxs = detector.findFaces(img, draw=False)

    if bboxs:
        #get the coordinate
        ws, hs = 1280, 720
        fx, fy = bboxs[0]["center"][0], bboxs[0]["center"][1]
        pos = [fx, fy]


        cv2.circle(img, (fx, fy), 80, (0, 0, 255), 2)
        cv2.putText(img, str(pos), (fx+15, fy-15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2 )
        cv2.line(img, (0, fy), (ws, fy), (0, 0, 0), 2)  # x line
        cv2.line(img, (fx, hs), (fx, 0), (0, 0, 0), 2)  # y line
        cv2.circle(img, (fx, fy), 15, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "TARGET LOCKED", (850, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3 )

    else:
        cv2.putText(img, "NO TARGET", (880, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
        cv2.circle(img, (640, 360), 80, (0, 0, 255), 2)
        cv2.circle(img, (640, 360), 15, (0, 0, 255), cv2.FILLED)
        cv2.line(img, (0, 360), (ws, 360), (0, 0, 0), 2)  # x line
        cv2.line(img, (640, hs), (640, 0), (0, 0, 0), 2)  # y line

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
