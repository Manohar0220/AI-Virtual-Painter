import math
import tkinter.dialog

import cv2
import numpy as np
import mediapipe as mp
import time
import HandTracking as htm
import os
import autopy
import pyautogui
from tkinter.filedialog import *
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


brushthickness=15
eraserthickness=100
xp=0
yp=0
cap = cv2.VideoCapture(0)
cap.set(3, 1366)
cap.set(4, 768)
#cap2 = cv2.VideoCapture(0)
#cap2.set(3, 400)
#cap2.set(4, 250)
head = cv2.imread(f'{"header"}/{"img1.png"}')  #layout image reading
drawcolor = (0,0,0)
detector = htm.HandDetector(detectionCon=0.85, maxHands=2)
imgcanvas=np.zeros((720,1280,3),np.uint8)
imgcanvas.fill(255)
#img_back=np.zeros((629,1280,3),np.uint8)
#img_back.fill(255)
wscr, hscr= pyautogui.size()
#print(wscr, hscr)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volrange=volume.GetVolumeRange()
#print(volrange)
minvol= volrange[0]
maxvol= volrange[1]
vol_control=0




while True:
    success, img = cap.read()
    img=cv2.flip(img,1)
    img = detector.findHands(img)
    #success, img2 = cap.read()
    #img2 = cv2.flip(img, 1)
    #img2 = detector.findHands(img)
    #hand detecting
    lmlist= detector.findPostion(img, draw=False)  # get position coordinates of the hand
    if len(lmlist)!=0:
        x1, y1 = lmlist[8][1:]  #taking cordinates of index and middle finger
        x2, y2 = lmlist[12][1:]
        xt, yt= lmlist[4][1:]
        cx, cy= (xt+x1)//2 ,(yt+y1)//2
        length= math.hypot(x1-xt, y1-yt)
        #print(length)
        #vol range= -74 to 0
        #length range= 50 - 350
        vol=np.interp(length, [50,350], [minvol,maxvol])

        fingers= detector.fingersUp()

        # print(fingers)
        if fingers is not None:
            if (fingers[1]==1 and fingers[2]==0) or (fingers[1]==1 and fingers[2]==1):
                x3= np.interp(x1, (0,1355), (0,wscr))
                y3 = np.interp(y1, (0,760), (0, hscr))
                autopy.mouse.move(x3,y3)

        if fingers is not None:
            if fingers[1] and fingers[2]:    #Selection mode
                xp,yp=0,0
                if y1<90:  #in header layout
                    if 100 < x1 < 172:
                        drawcolor=(0,0,0)
                        vol_control=0
                    elif 180 < x1 < 260:
                        drawcolor=(128,0,128)
                        vol_control = 0
                    elif 265 < x1 < 345:
                        drawcolor=(0,255,0)
                        vol_control = 0
                    elif 355 < x1 < 440:
                        drawcolor=(0,255,255)
                        vol_control = 0
                    elif 445 < x1 < 520:
                        drawcolor=(255,0,0)
                        vol_control = 0
                    elif 525 < x1 < 620:
                        drawcolor=(0,0,255)
                        vol_control = 0
                    elif 625 < x1 < 700:
                        drawcolor=(255,0,255)
                        vol_control = 0
                    elif 710 < x1 < 780:
                        drawcolor=(0,165,255)
                        vol_control = 0
                    elif 790 < x1 < 870:
                        drawcolor=(255,255,255)
                        vol_control = 0
                    elif 890 < x1 < 940:
                        brushthickness = 10
                        eraserthickness = 20
                        vol_control = 0
                    elif 941 < x1 < 1000:
                        brushthickness = 25
                        eraserthickness = 50
                        vol_control = 0
                    elif 1020 < x1 < 1100:
                        brushthickness = 50
                        eraserthickness = 100
                        vol_control = 0
                    elif 1110 < x1 < 1200:
                        vol_control=1


                cv2.rectangle(img, (x1, y1 - 10), (x2, y2 + 30), drawcolor, cv2.FILLED)

            elif fingers[1]:#Drawing mode
                if vol_control==0:
                    cv2.circle(img, (x1, y1), 15, drawcolor, cv2.FILLED)
                    if xp==0 and yp ==0:
                        xp,yp=x1,y1
                    if drawcolor==(255,255,255): # eraser
                        cv2.line(img, (xp, yp), (x1, y1), drawcolor, eraserthickness)
                        cv2.line(imgcanvas, (xp, yp), (x1, y1), drawcolor, eraserthickness)
                    else:
                        cv2.line(img,(xp,yp),(x1,y1),drawcolor, brushthickness)
                        cv2.line(imgcanvas, (xp, yp), (x1, y1), drawcolor, brushthickness)
                    xp,yp=x1,y1
                elif vol_control==1:
                    volume.SetMasterVolumeLevel(vol, None)

        if fingers is not None:
            if fingers[0]==0 and fingers[1]==0 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:
                myscreenshot=pyautogui.screenshot()
                save_work= asksaveasfilename()
                myscreenshot.save(save_work + '.png')

    imgGray=cv2.cvtColor(imgcanvas,cv2.COLOR_BGR2GRAY)
    _, imgInv=cv2.threshold(imgGray,50,255,cv2.THRESH_BINARY_INV)
    imgInv=cv2.cvtColor(imgInv,cv2.COLOR_GRAY2BGR)
    #img=cv2.bitwise_and(img,imgInv)
    #img=cv2.bitwise_or(img,imgcanvas)
    #img[0:93, 0:1235] = head #layout setup
    imgcanvas[0:93, 0:1235]=head
    #img[91:720, 0:1233]= img_back
    # img=cv2.addWeighted (img,0.5,imgcanvas,0.5,0)
    cv2.imshow("AI Virtual Controller", img)
    #cv2.imshow("Camera", img2)
    cv2.imshow("AI VIRTUAL PAINTER", imgcanvas)#displaying
    cv2.waitKey(1)