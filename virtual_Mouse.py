import os
import time
import cv2
import HandTrackingModule as htm
import numpy as np
import autopy

###########################
wCam, hCam = 1280, 720
wScreen, hScreen = autopy.screen.size()
hPad, wPad = 225,400
pXLocation, pYLocation = 0, 0
cXLocation, cYLocation = 0, 0
smoothvalue = 7
clicked = False
rightClicked = False

cTime = 0
pTime = 0
###########################
#pad ratio: 16:9, value: 400:225
#->

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)


filePath = "finger_img"
imgLst = os.listdir(filePath)

overlayLst = []
for imgPath in imgLst:
    img = cv2.imread(os.path.join(filePath, imgPath))
    overlayLst.append(img)

cTime = 0
pTime = 0

detector = htm.HandDetector()

print(dir(autopy.mouse))

while True:

    success, img = cap.read()
    img = cv2.flip(img, 1)
    detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        x1,y1 = lmList[8][1:]
        x2,y2 = lmList[12][1:]
        fingerLst = detector.countFingers()
        cv2.rectangle(img, (wCam - wPad - 50, hCam - hPad - 300),(wCam - 50, hCam - 300),(0,0,255),2)

        #mouse moving
        if fingerLst == [0,0,0,0,1]:
            if  (wCam - wPad - 50)<x1< (wCam -50) and (hCam - hPad - 300)< y1< ( hCam - 300):
                cv2.circle(img, (x1, y1), 10, (255,0,255), cv2.FILLED)
                #điều chỉnh toạ độ khi di tay trong cam với chuột trên màn hình
                x3= np.interp(x1,(wCam - wPad - 50,wCam -50 ),(0,wScreen))
                y3 = np.interp(y1,(hCam - hPad - 300, hCam - 300),(0,hScreen))
                #autopy.mouse.smooth_move(x3,y3) không dùng được vì nó làm chậm khung hình
                cXLocation = pXLocation +(x3 - pXLocation) / smoothvalue
                cYLocation = pYLocation + (y3 - pYLocation) / smoothvalue
                autopy.mouse.move(cXLocation,cYLocation)
                pXLocation, pYLocation = cXLocation, cYLocation
        #left Click
        if fingerLst == [0,0,1,0,1]:
            length,img, infoLst = detector.findDistance(img,8,12)
            if length < 40:
                if not clicked:
                    autopy.mouse.click()
                    clicked = True
                    cv2.circle(img, (infoLst[4], infoLst[5]), 10, (0,255,0), cv2.FILLED)
            else:
                clicked = False
        #right Click
        if fingerLst == [0,0,0,1,1]:
            length, img, infoLst = detector.findDistance(img, 4, 8)
            if length < 40:
                if not clicked:
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)
                    clicked = True
                    cv2.circle(img, (infoLst[4], infoLst[5]), 10, (0, 255, 0), cv2.FILLED)
            else:
                clicked = False
        # drag and drop will dev later - when i have energy and ideas

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    cv2.imshow('Video', img)
    cv2.waitKey(1)