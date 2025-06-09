import os
import time
import cv2
import HandTrackingModule as htm

wCam, hCam = 1280, 720

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


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lms = detector.findPosition(img)
    rightHand = []
    leftHand = []
    if len(lms) != 0:
        #right hand
        # if lms[0][1] < lms[1][1]:
        #     rightHand = detector.countFingers(lms)
        #
        # # left hand
        # elif lms[0][1] > lms[1][1]:
        Hand = detector.countFingers()

        if Hand == [0, 0, 0, 1, 1]:
            detector.volume_control(img)
            cv2.putText(img, "Vol Control", (15, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        totalFingers =Hand.count(1)
        # h, w, c = overlayLst[totalFingers].shape
        # img[0:h, 0:w] = overlayLst[totalFingers]
        cv2.rectangle(img, (10, 10), (210, 250), (255, 0, 0), 3)
        cv2.putText(img, str(totalFingers), (40, 170), cv2.FONT_HERSHEY_PLAIN, 15, (0, 0, 0), 5)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (1200, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    cv2.imshow('Image', img)
    cv2.waitKey(1)

