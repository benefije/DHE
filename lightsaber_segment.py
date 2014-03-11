# -*- coding: utf-8 -*-
"""
@author: quentin
@descript: We meet again, at last.
"""

import sys
import time
import cv,cv2
import almath
from naoqi import ALProxy
import numpy as np
import Image
import random
import math
import reset
import kmeans
import nao_live
import sharedMem
import threading as th

global motionProxy
global tts
global post
global sonarProxy
global memoryProxy
global IP
global PORT


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line2[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def swordcenterdetection(shm_tar, mutex_tar,enemy="obi",window=5,pb=0.7,segHough=50):
	global motionProxy
	global post
	global sonarProxy
	global memoryProxy
	global IP
	global PORT
	# work ! set current to servos
	stiffnesses  = 1.0
	time.sleep(0.5)

	# init video
	cameraProxy = ALProxy("ALVideoDevice", IP, PORT)
	resolution = 1    # 0 : QQVGA, 1 : QVGA, 2 : VGA
	colorSpace = 11   # RGB
	camNum = 0 # 0:top cam, 1: bottom cam
	fps = 1; # frame Per Second
	cameraProxy.setParam(18, camNum)
	try:
		videoClient = cameraProxy.subscribe("python_client", 
														resolution, colorSpace, fps)
	except:
		cameraProxy.unsubscribe("python_client")
		videoClient = cameraProxy.subscribe("python_client", 
														resolution, colorSpace, fps)
	print "Start videoClient: ",videoClient
	# Get a camera image.
	# image[6] contains the image data passed as an array of ASCII chars.
	naoImage = cameraProxy.getImageRemote(videoClient)
	imageWidth = naoImage[0]
	imageHeight = naoImage[1]

	found = True
	posx=0
	posy=0
	mem = cv.CreateMemStorage(0)
	i=0
	cv.NamedWindow("Real")
	cv.MoveWindow("Real",0,0)
	cv.NamedWindow("Threshold")
	cv.MoveWindow("Real",imageWidth+100,0)
	closing = 1
	tstp,tu=0,0
	K=2
	Mf,Mft = [],[]
	window = 5 # lenght of the window of observation for the low pass filter 
	pb = 0.7 # low pass filter value 
	print "before lines"
	try:
		while found:
			#Synchro
			mutex_tar.acquire()
			n = shm_tar.value[0]
			mutex_tar.release()
			if n==-1:
				print "Fail in target mem zone tar. Exit" , n
				
			elif n==-2:
				print "Terminated by parent"

			# Get current image (top cam)
			naoImage = cameraProxy.getImageRemote(videoClient)
			# Get the image size and pixel array.
			imageWidth = naoImage[0]
			imageHeight = naoImage[1]
			array = naoImage[6]
			# Create a PIL Image from our pixel array.
			pilImg = Image.fromstring("RGB", (imageWidth, imageHeight), array)
			# Convert Image to OpenCV
			cvImg = cv.CreateImageHeader((imageWidth, imageHeight),cv.IPL_DEPTH_8U, 3)
			cv.SetData(cvImg, pilImg.tostring())
			cv.CvtColor(cvImg, cvImg, cv.CV_RGB2BGR)
			hsv_img = cv.CreateImage(cv.GetSize(cvImg), 8, 3)
			cv.CvtColor(cvImg, hsv_img, cv.CV_BGR2HSV)
			thresholded_img =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			
			
			if enemy == "obi":
				# Get the blue on the image
				cv.InRangeS(hsv_img, (100, 40, 40), (150, 255, 255), thresholded_img)
			elif enemy == "dark":
				# Get the red on the image
				cv.InRangeS(hsv_img, (0, 150, 150), (40, 255, 255), thresholded_img)
			else:
				tts.say("I don't know my enemy")

			# cv.Erode(thresholded_img,thresholded_img, None, closing)
			# cv.Dilate(thresholded_img,thresholded_img, None, closing)
			storage = cv.CreateMemStorage(0)

			lines = cv.HoughLines2(thresholded_img, storage, cv.CV_HOUGH_PROBABILISTIC, 1, cv.CV_PI/180, segHough, param1=0, param2=0)
			lines_standard = cv.HoughLines2(thresholded_img, storage, cv.CV_HOUGH_STANDARD, 1, cv.CV_PI/180, segHough, param1=0, param2=0)
			Theta = []
			for l in lines_standard:
				Theta.append(l[1])
			theta = np.mean(Theta)
			PTx,PTy,Mftx,Mfty = [],[],[],[]

			for l in lines:
				pt1 = l[0]
				pt2 = l[1]
				cv.Line(cvImg, pt1, pt2, cv.CV_RGB(255,255,255), thickness=1, lineType=8, shift=0)
				PTx.append(pt1[0])
				PTx.append(pt2[0])
				PTy.append(pt1[1])
				PTy.append(pt2[1])
			if len(PTx)!=0:	
				xm = np.mean(PTx)
				ym = np.mean(PTy)
				M = (int(xm),int(ym))
				Mf.append(M)
				if len(Mf)>window:
					Mft = Mf[len(Mf)-window:len(Mf)]
					for m in Mft[0:-2]:
						Mftx.append(m[0])
						Mfty.append(m[1])
					mx = (1-pb)*np.mean(Mftx) + pb*Mftx[-1]
					my = (1-pb)*np.mean(Mfty) + pb*Mfty[-1]
					M = (int(mx),int(my))
					cv.Circle(cvImg,M,5,(254,0,254),-1)
					#Thread processing
					mutex_tar.acquire()
					shm_tar.value = [n,(M[0],M[1],0,theta)]
					mutex_tar.release()

			cv.ShowImage("Real",cvImg)
			cv.ShowImage("Threshold",thresholded_img)
			cv.WaitKey(1)

	except KeyboardInterrupt:
		print
		print "Interrupted by user, shutting down" 
		end()

def end():
	global motionProxy
	global post
	global sonarProxy
	global memoryProxy
	pNames = "Body"
	post.goToPosture("Crouch", 1.0)
	time.sleep(1.0)
	pStiffnessLists = 0.0
	pTimeLists = 1.0
	proxy = ALProxy("ALMotion",IP, 9559)
	proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)
	#tts.say("exit")
	print
	print "This is the END"
	cameraProxy.unsubscribe(videoClient)
	sys.exit(0)

def init():
	global motionProxy
	global tts
	global post
	global sonarProxy
	global memoryProxy
	global IP
	global PORT

	post = ALProxy("ALRobotPosture", IP, PORT)
	tts = ALProxy("ALTextToSpeech", IP, PORT)
	motionProxy = ALProxy("ALMotion", IP, PORT)
	sonarProxy = ALProxy("ALSonar", IP, PORT)
	sonarProxy.subscribe("myApplication")
	memoryProxy = ALProxy("ALMemory", IP, PORT)
	post.goToPosture("StandInit", 1.0)
	time.sleep(2)

def main(shm_tar, mutex_tar,IPf,enemy):
	global IP
	global PORT
	IP = IPf
	PORT = 9559
	init()
	swordcenterdetection(shm_tar, mutex_tar,enemy)

if __name__ == "__main__":
	IP = "172.20.12.26"
	PORT = 9559
	# Read IP address from first argument if any.
	if len(sys.argv) > 1:
		IP = sys.argv[1]
	if len(sys.argv) > 2:
		IP = sys.argv[1]
		enemy = sys.argv[2]
	main(IP,PORT,enemy)
	