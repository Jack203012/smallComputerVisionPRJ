import cv2
import mediapipe as mp
import time
import math
import numpy as np
import autopy


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

wCam, hCam = 1280, 720


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
        self.tipsId = [20, 16, 12]


        self.wScreen, self.hScreen = autopy.screen.size()
        self.hPad, self.wPad = 225, 400
        self.pXLocation, self.pYLocation = 0, 0
        self.cXLocation, self.cYLocation = 0, 0
        self.smoothvalue = 7
        self.clicked = False


    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.Hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo = 0):
        self.lms = []
        if self.results.multi_hand_landmarks:
            Hands = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hands.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lms.append([id, cx, cy])
        return self.lms


    def volume_control(self, img):
        x1, y1 = self.lms[4][1], self.lms[4][2]
        x2, y2 = self.lms[8][1], self.lms[8][2]
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        lenght = math.hypot(x2 - x1, y2 - y1)

        # minlength = 20,  maxlength = 200
        # min vol = -65, max vol = 0
        vol = np.interp(lenght, [20, 200], [minVolume, maxVolume])
        volPerc = np.interp(lenght, [20, 200], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)
        #cv2.putText(img, f'{int(volPerc)} %', (600, 50),cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    def findDistance(self, img, no1Finger =0, no2Finger=0, draw=True):
        x1, y1 = self.lms[no1Finger][1], self.lms[no1Finger][2]
        x2, y2 = self.lms[no2Finger][1], self.lms[no2Finger][2]
        length = math.hypot(x2 - x1, y2 - y1)
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(img, ((x1+x2)//2,(y1+y2)//2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
        return length, img, [x1,y1,x2,y2, (x1+x2)//2,(y1+y2)//2 ]
    def countFingers(self):

        #check trước 3 ngón sau cùng lần lượt là út -> áp út -> giữa
        finger = []
        for tip in self.tipsId:
            if self.lms[tip][2] < self.lms[tip - 2][2]:
                finger.append(1)
            else:
                finger.append(0)
        #left và right là để check tay trái tay phải.
        #trong 2 hàm check đó sẽ check xem ngón cái có đưa lên hay k
        #left
        if self.lms[0][1] < self.lms[1][1]:
            if self.lms[4][1] > self.lms[5][1] and self.lms[4][1] > self.lms[2][1]:
                finger.append(1)
            else:
                finger.append(0)
        #right
        elif self.lms[0][1] > self.lms[1][1]:
            if self.lms[4][1] < self.lms[5][1] and self.lms[4][1] < self.lms[2][1]:
                finger.append(1)
            else:
                finger.append(0)
        # check ngón cái rồi mới check ngón trỏ :))))))))))
        # đm logic check ngu vl
        if finger == [0, 0, 0, 1]:
            if self.lms[8][2] < self.lms[5][2]:
                finger.append(1)
            else:
                finger.append(0)
        else:
            if self.lms[8][2] < self.lms[6][2]:
                finger.append(1)
            else:
                finger.append(0)
        return finger
    def virtual_Mouse(self, img,fingerLst = [] ):
        x1, y1 = self.lms[8][1:]
        x2, y2 = self.lms[12][1:]
        cv2.rectangle(img, (wCam - self.wPad - 50, hCam - self.hPad - 300), (wCam - 50,hCam - 300), (0, 0, 255), 2)

        # mouse moving
        if fingerLst == [0, 0, 0, 0, 1]:
            if (wCam - self.wPad - 50) < x1 < (wCam - 50) and (hCam - self.hPad - 300) < y1 < (hCam - 300):
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                # điều chỉnh toạ độ khi di tay trong cam với chuột trên màn hình
                x3 = np.interp(x1, (wCam -self.wPad - 50, wCam - 50), (0, self.wScreen))
                y3 = np.interp(y1, (hCam - self.hPad - 300, hCam - 300), (0, self.hScreen))
                # autopy.mouse.smooth_move(x3,y3) không dùng được vì nó làm chậm khung hình
                self.cXLocation = self.pXLocation + (x3 - self.pXLocation) / self.smoothvalue
                self.cYLocation = self.pYLocation + (y3 - self.pYLocation) / self.smoothvalue
                autopy.mouse.move(self.cXLocation, self.cYLocation)
                self.pXLocation, self.pYLocation = self.cXLocation, self.cYLocation
        # left Click
        if fingerLst == [0, 0, 1, 0, 1]:
            length, img, infoLst = self.findDistance(img, 8, 12)
            if length < 40:
                if not self.clicked:
                    autopy.mouse.click()
                    self.clicked = True
                    cv2.circle(img, (infoLst[4], infoLst[5]), 10, (0, 255, 0), cv2.FILLED)
            else:
                self.clicked = False
        # right Click
        if fingerLst == [0, 0, 0, 1, 1]:
            length, img, infoLst = self.findDistance(img, 4, 8)
            if length < 40:
                if not self.clicked:
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)
                    self.clicked = True
                    cv2.circle(img, (infoLst[4], infoLst[5]), 10, (0, 255, 0), cv2.FILLED)
            else:
                self.clicked = False

def main():
    cTime = 0
    pTime = 0
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = HandDetector()
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lms = detector.findPosition(img)
        if len(lms)!=0 :
            finger = detector.countFingers()
            detector.virtual_Mouse(img,finger)
            cv2.putText(img, str(finger.count(1)), (100, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        cv2.imshow('Image', img)
        cv2.waitKey(1)




if __name__ == "__main__":
    main()