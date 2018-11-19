#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue
import time



class extractFrames(threading.Thread):
    def __init__(self,fileName, outputBuffer):
        threading.Thread.__init__(self)
        self.fileName = fileName
        self.outputBuffer = outputBuffer

    def run(self):    
    # Initialize frame count 
        count = 0

        # open video file
        vidcap = cv2.VideoCapture(self.fileName)

        # read first image
        success,image = vidcap.read()
        
        print("Reading frame {} {} ".format(count, success))
        while success:
            # get a jpg encoded frame
            success, jpgImage = cv2.imencode('.jpg', image)

            #encode the frame as base 64 to make debugging easier
            jpgAsText = base64.b64encode(jpgImage)

            # add the frame to the buffer
            self.outputBuffer.put(jpgAsText)
            while self.outputBuffer.full():
                time.sleep(0.0000020)
        
            success,image = vidcap.read()
            print('Reading frame {} {}'.format(count, success))
            count += 1

        print("Frame extraction complete")

class convertToGray(threading.Thread):
    def __init__(self, inputBuffer, outputBuffer):
        self.inputBuffer = inputBuffer
        self.outputBuffer = outputBuffer

    def run(self):
        count = 0

        # get the next frame file name
        while not self.inputBuffer.empty():
            frameAsText = self.inputBuffer.get()

            # decode the frame 
            jpgRawImage = base64.b64decode(frameAsText)

            # convert the raw frame to a numpy array
            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
            
            # load the next file
            inputFrame = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)

            while inputFrame is not None:
            # convert the image to grayscale
                grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
                print("Converting frame {}".format(count))
                # generate output file name

                success, jpgImage = cv2.imencode('.jpg', grayscaleFrame)

                #encode the frame as base 64 to make debugging easier
                jpgAsText = base64.b64encode(jpgImage)
                self.outputBuffer.put(jpgAsText)
                while self.outputBuffer.full():
                    time.sleep(0.0000024)

            count += 1

            # generate input file name for the next frame)

            
class displayFrames(threading.Thread):
    def __init__(self, inputBuffer):
        self.inputBuffer = inputBuffer

    def run(self):
        # initialize frame count
        count = 0

        # go through each frame in the buffer until the buffer is empty
        while not self.inputBuffer.empty():
            # get the next frame
            frameAsText = self.inputBuffer.get()

            # decode the frame 
            jpgRawImage = base64.b64decode(frameAsText)

            # convert the raw frame to a numpy array
            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
            
            # get a jpg encoded frame
            img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

            print("Displaying frame {}".format(count))        

            # display the image in a window called "video" and wait 42ms
            # before displaying the next frame
            cv2.imshow("Video", img)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1

        print("Finished displaying all frames")
        # cleanup the windows
        cv2.destroyAllWindows()


filename = 'clip.mp4'

# shared queue  
extractionQueue = queue.Queue(10)
readFrames = extractFrames(filename, extractionQueue)

# extract the frames
#extractFrames(filename,extractionQueue)

# display the frames
#displayFrames(extractionQueue)
displayFrame = displayFrames(extractionQueue)

readFrames.start()

displayFrame.start()
