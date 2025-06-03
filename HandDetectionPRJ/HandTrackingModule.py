import cv2
import mediapipe as mp
import time
import math
import numpy as np


from pycaw.api.endpointvolume import IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volumeRange = volume.GetVolumeRange()
maxVolume = volumeRange[1]
minVolume = volumeRange[0]
volPerc = 0

class HandDetector:
    def __init__(self, mode = False, maxHands = 2, detectionConf = 0.5, trackConf = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionConf = detectionConf
        self.trackConf = trackConf

        self.mpHands = mp.solutions.hands
        self.Hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionConf,
            min_tracking_confidence=self.trackConf
        )
        self.mpDraw = mp.solutions.drawing_utils


    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.Hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo = 0):
        lmsLst = []
        if self.results.multi_hand_landmarks:
            Hands = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hands.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmsLst.append([id, cx, cy])
        return lmsLst


    def volume_control(self, img, lms = []):
        x1, y1 = lms[4][1], lms[4][2]
        x2, y2 = lms[8][1], lms[8][2]
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        lenght = math.hypot(x2 - x1, y2 - y1)

        # minlength = 20,  maxlength = 200
        # min vol = -65, max vol = 0
        vol = np.interp(lenght, [20, 200], [minVolume, maxVolume])
        volPerc = np.interp(lenght, [20, 200], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)
        cv2.putText(img, f'{int(volPerc)} %', (600, 50),cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)



def main():
    cTime = 0
    pTime = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lms = detector.findPosition(img)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        cv2.imshow('Image', img)
        cv2.waitKey(1)




if __name__ == "__main__":
    main()