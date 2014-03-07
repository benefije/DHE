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

global motionProxy
global tts
global post
global sonarProxy
global memoryProxy

def rockandload(fighter):
	global motionProxy
	global post
	if fighter=="obi":
		tts.say("I need my blue lightsaber")
	if fighter=="dark":
		tts.say("I need my red lightsaber")
	names  = ["RHand", "LHand"]
	angles = [1,1]
	fractionMaxSpeed  = 0.2
	motionProxy.setAngles(names, angles, fractionMaxSpeed)
	time.sleep(3)
	angles = [0.15,0.15]
	motionProxy.setAngles(names, angles, fractionMaxSpeed)
	time.sleep(1)

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


def clustering(data,cvImg,nframe,error,K=2):
	flag1=0
	flag2=0
	l0=0
	l1=0

	centroid, labels=np.array([]),np.array([])
	if len(data)>1:
		dataarray = np.asarray(data)
		centroid, labels = kmeans.kMeans(dataarray, K, maxIters = 20, plot_progress = None)  

		try:
			cv.Line(cvImg,(int(centroid[0][0]),int(centroid[0][1])),(int(centroid[1][0]),int(centroid[1][1])),(255,0,0))
			cv.Circle(cvImg,int(centroid[0][0]),int(centroid[0][1]),5,(0,255,0),-1)
		except:
			per=False
		i=0
		for l in labels:
			if l==0:
				l0=l0+1
			if l==1:
				l1=l1+1

		if l1>l0:
			temp = centroid[0]
			centroid[0] = centroid[1]
			centroid[1] = temp
			for l in labels:
				if l==0:	
					cv.Circle(cvImg,(data[i][0],data[i][1]),5,(254,0,254),-1)
					flag1=1
				if l==1:			
					cv.Circle(cvImg,(data[i][0],data[i][1]),5,(0,255,255),-1)
					flag2=1
				i=i+1
		else:
			for l in labels:
				if l==0:				
					cv.Circle(cvImg,(data[i][0],data[i][1]),5,(0,255,255),-1)
					flag1=1
				if l==1:		
					cv.Circle(cvImg,(data[i][0],data[i][1]),5,(254,0,254),-1)
					flag2=1
				i=i+1
		try:
			cv.Circle(cvImg,(int(centroid[0][0]),int(centroid[0][1])),5,(0,255,0),-1)
		except:
			per=False
		if(flag1 + flag2<2):
			error=error+1
			pcterror = (error/nframe)*100.0
			#print "current error of kmeans = ",pcterror,"%"          	
	return cvImg,error,centroid, labels

def meet(fighter):
	global motionProxy
	global post
	global sonarProxy
	global memoryProxy
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
	error=0.0
	nframe=0.0
	closing = 1
	tstp,tu=0,0
	K=2
	try:
		while found:
			nframe=nframe+1
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
			thresholded_img2 =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			temp =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			eroded =  cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			skel = cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			img = cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			edges = cv.CreateImage(cv.GetSize(hsv_img), 8, 1)
			# Get the orange on the image
			cv.InRangeS(hsv_img, (110, 80, 80), (150, 200, 200), thresholded_img)
			#cv.InRangeS(hsv_img, (110, 80, 80), (150, 200, 200), thresholded_img2)
			storage = cv.CreateMemStorage(0)
			#contour = cv.FindContours(thresholded_img, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
			#cv.Smooth(thresholded_img, thresholded_img, cv.CV_GAUSSIAN, 3, 3)
			# cv.Erode(thresholded_img,thresholded_img, None, closing)
			# cv.Dilate(thresholded_img,thresholded_img, None, closing)
			# cv.CvtColor(thresholded_img, thresholded_img, cv.CV_HSV2BGR)
			# cv.CvtColor(thresholded_img, thresholded_img, cv.CV_BGR2GRAY)
			# cv.Sobel(thresholded_img, thresholded_img, 1, 0, apertureSize=3)
			# cv.Canny(thresholded_img, thresholded_img, threshold1, threshold2, aperture_size=3)

			lines = cv.HoughLines2(thresholded_img, storage, cv.CV_HOUGH_STANDARD, 1, cv.CV_PI/180, 120, param1=0, param2=0)

			#cv.Canny(thresholded_img, edges, 10, 100, aperture_size=3)
			first = 1
			sl=0
			for l in lines:
				sl=sl+1
			# for l in lines:
			Mx=[]
			My=[]
			for l in lines:
				
				rho = l[0]
				theta = l[1]
				#print rho,theta
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				cf1,cf2  = 300,300
				xpt11 = int(cv.Round(x0 + cf1*(-b)))
				ypt11 = int(cv.Round(y0 + cf1*(a)))
				xpt12 = int(cv.Round(x0 - cf2*(-b)))
				ypt12 = int(cv.Round(y0 - cf2*(a)))
				pt11 = (xpt11,ypt11)
				pt12 = (xpt12,ypt12)
				cv.Line(cvImg, pt11, pt12, cv.CV_RGB(255,255,255), thickness=1, lineType=8, shift=0)
				B = np.array(((xpt11,ypt11),(xpt12,ypt12)))

				try:		
					mx,my = line_intersection(A, B)
					print "m",(mx,my)
					Mx.append(mx)
					My.append(my)
					
				except:
					noprint=0


				rho = l[0]
				theta = l[1]
				#print rho,theta
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				cf1,cf2  = 300,300
				xpt1 = int(cv.Round(x0 + cf1*(-b)))
				ypt1 = int(cv.Round(y0 + cf1*(a)))
				xpt2 = int(cv.Round(x0 - cf2*(-b)))
				ypt2 = int(cv.Round(y0 - cf2*(a)))
				A = np.array(((xpt1,ypt1),(xpt2,ypt2)))
				#  and (xpt2>imageHeight or xpt2<0) and (ypt2>imageWidth or ypt2<0)
				# and (not (0>ypt1>imageWidth) and not(0>ypt2>imageWidth)))
				# while ((not (0>xpt1) or not (xpt1<imageHeight) )):		
				# 	cf1 = cf1 - 50
				# 	cf2 = cf2 + 50
				# 	xpt1 = cv.Round(x0 + cf1*(-b))
				# 	ypt1 = cv.Round(y0 + cf1*(a))
				# 	xpt2 = cv.Round(x0 - cf2*(-b))
				# 	ypt2 = cv.Round(y0 - cf2*(a))
				
				
				X = np.array(())
				
				A = cv.CreateMat(2, 2, cv.CV_32FC1)
				B = cv.CreateMat(2, 2, cv.CV_32FC1)
				X =  cv.CreateMat(2, 2, cv.CV_32FC1)
				cv.mSet(A, 1, 1, xpt11),cv.mSet(A, 1, 2, ypt11),cv.mSet(A, 2, 1, xpt12),cv.mSet(A, 2, 2, ypt12)
				cv.mSet(B, 1, 1, xpt1),cv.mSet(B, 1, 2, ypt1),cv.mSet(B, 2, 1, xpt2),cv.mSet(B, 2, 2, ypt2)

				cv.Solve(A, B, X, method=cv.CV_LU)
				x = np.asarray(X)

				pt1 = (xpt1,ypt1)
				pt2 = (xpt2,ypt2)
				xm = abs(cv.Round((xpt1 - xpt2)/2.0))
				ym = abs(cv.Round((ypt1 - ypt2)/2.0))
				cv.Line(cvImg, pt1, pt2, cv.CV_RGB(255,255,255), thickness=1, lineType=8, shift=0)

				mx,my = line_intersection(A, B)
				print "m",(mx,my)
				Mx.append(mx)
				My.append(my)
					
					
			print "len",len(Mx)
			if len(Mx)!=0:
				print "M",M
				Mm = (int(np.mean(Mx)),int(np.mean(My)))
				cv.Circle(cvImg,Mm,5,(254,0,254),-1)
			# cv.Smooth(thresholded_img2, thresholded_img2, cv.CV_GAUSSIAN, 3, 3)
			# cv.Erode(thresholded_img2,thresholded_img2, None, closing)
			# cv.Dilate(thresholded_img2,thresholded_img2, None, closing)


			# while( t<10):
			#     cv.Erode(thresholded_img,eroded, None, closing)
			#     cv.Erode(thresholded_img,img, None, closing)
			#     cv.Dilate(thresholded_img,temp, None, closing)

			#     cv.Sub(thresholded_img, temp, temp, mask=None)
			#     cv.Or(skel, temp, skel, mask=None)

			#     zeros = size - cv.CountNonZero(img)
			#     t=t+1
			#     #print zeros
			#     if zeros==size:
			#         done = True



			# storage = cv.CreateMemStorage(0)
			# contour = cv.FindContours(thresholded_img, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
			# points = [] 

			# d=[]
			# data=[]
			# while contour:			
			# 	# Draw bounding rectangles
			# 	bound_rect = cv.BoundingRect(list(contour))
			# 	contour = contour.h_next()
			# 	# for more details about cv.BoundingRect,see documentation
			# 	pt1 = (bound_rect[0], bound_rect[1])
			# 	pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
			# 	points.append(pt1)
			# 	points.append(pt2)
			# 	cv.Rectangle(cvImg, pt1, pt2, cv.CV_RGB(255,0,0), 1)
			# 	lastx=posx
			# 	lasty=posy
			# 	posx=cv.Round((pt1[0]+pt2[0])/2)
			# 	posy=cv.Round((pt1[1]+pt2[1])/2)
			# 	data.append([posx,posy])
			# 	d.append(math.sqrt(pt1[0]**2+pt2[0]**2))
			# 	d.append(math.sqrt(pt1[1]**2+pt2[1]**2))

			# cvImg,error,centroid,labels = clustering(data,cvImg,nframe,error,K)
			# # Update the closing size towards the number of found labels
			# if labels.size<2:
			# 	closing=1
			# if labels.size<6:
			# 	closing = 2
			# if labels.size>10:
			# 	closing=3
			# if closing < 1:
			# 	closing = 0



			cv.ShowImage("Real",cvImg)
			# cv.ShowImage("skel",skel)
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

def init(IP,PORT):
	global motionProxy
	global tts
	global post
	global sonarProxy
	global memoryProxy

	post = ALProxy("ALRobotPosture", IP, PORT)
	tts = ALProxy("ALTextToSpeech", IP, PORT)
	motionProxy = ALProxy("ALMotion", IP, PORT)
	sonarProxy = ALProxy("ALSonar", IP, PORT)
	sonarProxy.subscribe("myApplication")
	memoryProxy = ALProxy("ALMemory", IP, PORT)
	post.goToPosture("Crouch", 1.0)
	# time.sleep(2)


if __name__ == "__main__":
	IP = "172.20.12.26"
	PORT = 9559
	# Read IP address from first argument if any.
	if len(sys.argv) > 1:
		IP = sys.argv[1]
	if len(sys.argv) > 2:
		IP = sys.argv[1]
		fighter = sys.argv[2]

	init(IP,PORT)
	#rockandload(fighter)
	meet(fighter)