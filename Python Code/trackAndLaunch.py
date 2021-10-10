import faceDetect
import panTiltControl as ptc
from time import sleep
import cv2
from imutils.video import VideoStream

## Start video stream ##
vs = VideoStream(usePiCamera=True).start()
sleep(2) #camera warmup time

##Define pan/tilt ranges and initial values
panRange = [-45,45]
panInit = 0 #Initial value. Servo will be moved there in a later line
tiltRange = [80,140]
tiltInit = 110 #Stepper defaults to 0 upon being turned on

##Initialise variable to track motor status
motorStatus = 0
motorWarmup = 0

##Define haarcascade file path
haarPath = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

##Capture a test frame to establish frame size
frame = vs.read()
frameSize = frame.shape[:2]
centreX = frameSize[1]//2
centreY = frameSize[0]//2

#Initialise PID controller
pidPan = ptc.PID(kP=0.1, kD = 0.1)
pidTilt = ptc.PID(kP=0.1)
pidPan.initialise()
pidTilt.initialise()

#Initialise launcher object
launcher = ptc.Launcher()
launcher.connect()
launcher.pan(panInit)
panAngle = panInit
launcher.tilt(tiltInit)
tiltAngle = tiltInit
launcher.motor(motorStatus)

##Infinite loop while tracking
while True:
    #get a frame
    frame = vs.read()
    #convert frame to grayscale for use by haar cascade
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #check frame for faces
    [faceX, faceY, faceData] = faceDetect.findFace(frame, haarPath)
    
        
    #display current frame
    # Draw a rectangle around the faces
    if faceData is not None:
        print(panAngle,tiltAngle)
        (x, y, w, h) = faceData
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.putText(frame, "INTRUDER DETECTED!", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
        
        #calculate difference between frame centre and face centre
        error = [centreX-faceX,centreY-faceY]
        #get pid outputs
        panErr = pidPan.update(error[0])
        tiltErr = pidTilt.update(error[1])
        print("Face coords: " + str([faceX, faceY]))
        print("Goal coords: " + str([centreX, centreY]))
        #print("Error: "+ str([panErr,tiltErr]))
        newTilt = tiltAngle - tiltErr
        newPan = panAngle + panErr
        #move servos to that position
        if ptc.in_range(newTilt, tiltRange[0], tiltRange[1]):
            launcher.tilt(newTilt)
            tiltAngle = newTilt #update current tilt angle
        else: #target out of range. Return to default
            launcher.tilt(tiltInit)
            tiltAngle = tiltInit
            
        if ptc.in_range(newPan, panRange[0], panRange[1]):            
            launcher.pan(newPan)
            panAngle = newPan #update current pan angle
        else: #return to initial position
            launcher.pan(panInit)
        
        ## Determine whether to turn on motors or shoot
        #Fire if face centre is within 4 pixels of centre (diagonal distance)
        if ((centreX-faceX)**2 + (centreY-faceY)**2) < 4**2 and motorWarmup > 2:
            #motorWarmup makes sure the motors have had enough time to get up to speed
            launcher.load()
            cv2.putText(frame, "FIRE!", (120,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
        #Turn on motors if a face is within 15 pixels of centre (diagonal distance)
        if ((centreX-faceX)**2 + (centreY-faceY)**2) < 15**2:
            motorWarmup += 1
            if motorStatus == 0:
            #Don't waste time sending motor on signal if already on
                launcher.motor(1)
                motorStatus = 1
        elif ((centreX-faceX)**2 + (centreY-faceY)**2) >= 15**2 and motorStatus == 1:
            launcher.motor(0)
            motorStatus = 0
            motorWarmup = 0 #Will need to warm up again when switched on
    else: #no face detected
        launcher.motor(0)
        motorStatus = 0
        motorWarmup = 0
        #The above accounts for when a face goes from centred to missing,
            #which can cause the motors to stay on

    #display output
    cv2.namedWindow("Vid stream", cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vid stream', 600,600)
    cv2.imshow("Vid stream", frame)
    cv2.waitKey(1)
    
    
    