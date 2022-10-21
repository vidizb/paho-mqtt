import cv2
import numpy as np
import av
import mediapipe as mp
import streamlit as st
import paho.mqtt.client as mqtt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

    


broker = "test.mosquitto.org"
topic = "Vidi/ServoX"
client = mqtt.Client()
client.connect(broker)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mpHand = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHand.Hands(min_detection_confidence=0.8)
hands = mpHand.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
ws, hs = 1280, 720

def process(img):
    img.flags.writeable = False
    img = cv2.flip(img, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    
    x, y = 100, 100
    w, h = 200, 200
    X, Y = 120, 150
    
    cv2.rectangle(img, (x, y), (w, h), (0, 255, 255), cv2.FILLED)
    cv2.rectangle(img, (x + 120, y), (w + 120, h), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(img, (x + 240, y), (w + 240, h), (255, 0, 255), cv2.FILLED)

    multiHandDetection = results.multi_hand_landmarks #Hand Detection
    lmList = []
    
    counter_R, counter_G, counter_B = 0, 0, 0
    R_on, G_on, B_on = False, False, False 

    if multiHandDetection:
        #Hand Visualization
        for id, lm in enumerate(multiHandDetection):
            mpDraw.draw_landmarks(img, lm, mpHand.HAND_CONNECTIONS,
                                  mpDraw.DrawingSpec(color=(0, 255,255), thickness=4, circle_radius=7),
                                  mpDraw.DrawingSpec(color=(0, 0, 0), thickness = 4))

        #Hand Tracking
        singleHandDetection = multiHandDetection[0]
        for lm in singleHandDetection.landmark:
            h, w, c = img.shape
            lm_x, lm_y = int(lm.x*w), int(lm.y*h)
            lmList.append([lm_x, lm_y])

        print(lmList)

        # draw point
        myLP = lmList[8]
        px, py = myLP[0], myLP[1]
        cv2.circle(img, (px, py), 15, (255, 0, 255), cv2.FILLED)
        cv2.putText(img, str((px, py)), (px + 10, py - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
        cv2.line(img, (0, py), (ws, py), (0, 0, 0), 2)  # x line
        cv2.line(img, (px, hs), (px, 0), (0, 0, 0), 2)  # y line

        # convert position to degree value

     
        
        if x < px < 200 and y < py < 200:
            counter_R += 1
            if counter_R == 1:
                R_on = not R_on
        else:
            counter_R = 0
            if R_on:
                cv2.putText(img, "ON", (X, Y), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 255), 5)
            else:
                cv2.putText(img, "OFF", (X , Y), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 255), 5)
        
        if 220 < px < 320 and y < py < 200:
            counter_G += 1
            if counter_G == 1:
                G_on = not G_on
        else:
            counter_G = 0
            if G_on:
                cv2.putText(img, "ON", (X + 120, Y), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 255), 5)
            else:
                cv2.putText(img, "OFF", (X + 120, Y), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 255), 5)
        
        if 340 < px < 440 and y < py < 200:
            counter_B += 1
            if counter_B == 1:
                B_on = not B_on
        else:
            counter_B = 0
            if B_on:
                cv2.putText(img, "ON", (X + 240, Y), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 255), 5)
            else:
                cv2.putText(img, "OFF", (X + 240, Y), cv2.FONT_HERSHEY_PLAIN,
                            2, (0, 0, 255), 5)
        
        lastData = "-"
        val = str(counter_R) + str(counter_G) + str(counter_B)
        print(val)
        client.publish(topic, val)
        

        if lastData != val:
            client.publish(topic, val)
            lastData = val
            
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
