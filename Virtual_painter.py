import os
import numpy as np
import HandTrackingModule as htm
import time
import cv2

####################
thickness = 5
canvas = np.zeros((720, 1280, 3), np.uint8)
xp,yp = 0,0
eraserThickness = 75
###################


folderPath = "Virtual_Painter_Header"
myList = os.listdir(folderPath)
overlayLst = []
for imgPath in myList:
    img = cv2.imread(os.path.join(folderPath, imgPath))
    overlayLst.append(img)

header = overlayLst[0]
status = ['Gesture','Mouse','Red', 'Green', 'Blue', 'Eraser']
drawingColor =(0, 0, 255) #red
view_Status = status[0]

###################
wCam = 1280
hCam = 720
###################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.HandDetector()
while True:

    success, img = cap.read()
    img = cv2.flip(img, 1)
    detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        x1,y1 = lmList[8][1:]
        x2,y2 = lmList[12][1:]

        fingerLst = detector.countFingers()
        print(fingerLst)

        #để hiểu thì qua đọc note bên module nha :)
        if fingerLst == [0,0,1,0,1]:
            cv2.rectangle(img,(x1,y1-20),(x2,y2+20),(255,255,255),cv2.FILLED)
            #150 - 270  => cử chỉ tay
            #350 - 470 => di chuyển chuột
            #570-690 => cọ vẽ màu đỏ
            #755-875 => cọ màu lục
            #950-1070 => cọ màu xanh lam
            #1140 - 1250 => xoá
            if y1 < 80:
                if 150 <x1 <270: #hand gesture
                    header = overlayLst[0]
                    view_Status = status[0]
                if 350 <x1 <470: #mouse control
                    header = overlayLst[1]
                    view_Status = status[1]
                if 570 <x1 <690: #red brush
                    header = overlayLst[2]
                    view_Status = status[2]
                    drawingColor = (0, 0, 255)
                elif 755 <x1 < 875: #green brush
                    header = overlayLst[3]
                    view_Status = status[3]
                    drawingColor = (0, 255, 0)
                elif 950 < x1 < 1070: #blue brush
                    header = overlayLst[4]
                    view_Status = status[4]
                    drawingColor = (255, 0, 0)
                elif 1140 < x1 < 1250: #eraser
                    header = overlayLst[5]
                    view_Status = status[5]
                    drawingColor = (0, 0, 0)
        if view_Status =='Gesture':
            if fingerLst == [0, 0, 0, 1, 1]:
                detector.volume_control(img)
                cv2.putText(img, "Vol Control", (85, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        elif view_Status =='Mouse':
            detector.virtual_Mouse(img,fingerLst)
        else:
            if   fingerLst == [0,0,0,0,1]:
                cv2.circle(img,(x1,y1),10,drawingColor,cv2.FILLED)
                if xp ==0 and yp == 0:
                    xp,yp = x1,y1
                if drawingColor == (0,0,0):
                    cv2.line(img, (xp, yp), (x1, y1), drawingColor, eraserThickness)
                    cv2.line(canvas, (xp, yp), (x1, y1), drawingColor, eraserThickness)
                else:
                    cv2.line(img,(xp,yp),(x1,y1),drawingColor,thickness)
                    cv2.line(canvas, (xp, yp), (x1, y1), drawingColor, thickness)
                xp,yp = x1,y1
            else:
                xp, yp = 0, 0


    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInvert = cv2.threshold(imgGray, 127, 255, cv2.THRESH_BINARY_INV)
    imgInvert = cv2.cvtColor(imgInvert, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img,imgInvert)
    img = cv2.bitwise_or(img, canvas)


    img[0:80, 0:1280] = header
    cv2.putText(img, view_Status, (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    cv2.imshow('Video', img)
    cv2.waitKey(1)

