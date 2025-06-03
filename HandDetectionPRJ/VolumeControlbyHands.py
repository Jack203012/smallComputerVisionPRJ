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

tipsId = [20, 16, 12]
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lms = detector.findPosition(img)

    if len(lms) != 0:
        finger=[]
        for tip in tipsId:
            if lms[tip][2] < lms[tip - 2][2]:
                finger.append(1)
            else:
                finger.append(0)

        #right hand
        if lms[0][1] < lms[1][1]:
            if (lms[4][1] > lms[5][1] and lms[4][1] > lms[3][1]):
                finger.append(1)
            else:
                finger.append(0)
        # left hand
        elif lms[0][1] > lms[1][1]:
            if (lms[4][1] < lms[5][1] and lms[4][1] < lms[3][1]):
                finger.append(1)
            else:
                finger.append(0)

        if finger == [0,0,0,1]:
            if lms[8][2] < lms[5][2]:
                finger.append(1)
            else:
                finger.append(0)
        else:
            if lms[8][2] < lms[6][2]:
                finger.append(1)
            else:
                finger.append(0)

        if finger==[0,0,0,1,1] :
            detector.volume_control(img, lms)
            cv2.putText(img, "Vol Control", (15, 230), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        totalFingers = finger.count(1)
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

