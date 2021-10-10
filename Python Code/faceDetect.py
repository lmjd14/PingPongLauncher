#Written by: Logan Davis 2021
#Inspired by: https://www.pyimagesearch.com/2019/04/01/pan-tilt-face-tracking-with-a-raspberry-pi-and-opencv/

import cv2

def findFace(frame, haarCascade):
    ### Takes an image and path to a haarcascade file and returns position of face in image (if any)
    
    #Set up face detection cascade from given cascade file
    faceCascade = cv2.CascadeClassifier(haarCascade)
    #convert input frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Find faces in image
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.05, minNeighbors = 9, minSize = (30,30))
    
    #First check if there is a face in the image
    if len(faces) > 0:
        #If multiple faces are detected, use first face in list
        (x,y,w,h) = faces[0]
        faceX = int(x + (w/2.0)) #x pixel of face centre
        faceY = int(y + (h/2.0)) #y pixel of face centre
        
        return [faceX, faceY, faces[0]] #will only use faceX and faceY. faces[0] returned for extra info just in case
    else: #no faces found
        return [None, None, None] #This output is handled upstream