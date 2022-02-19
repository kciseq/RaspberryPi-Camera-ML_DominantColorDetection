import io
import time
import picamera
from PIL import Image
import cv2 as cv
import numpy as np
import serial


def outputs():
    stream = io.BytesIO()
    for i in range(6):
        # This returns the stream for the camera to capture to
        yield stream
        K = 6
        stream.seek(0)
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        image = cv.imdecode(data, 1) # remember that it's in BGR format
        Z = image[y1:y2, x1:x2].reshape((-1,3))
        # convert to np.float32
        Z = np.float32(Z)
        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 4, 1.0)

        
        ret,label,center=  cv.kmeans(Z,K,None,criteria,1,cv.KMEANS_RANDOM_CENTERS)
        # Now convert back into uint8, and make original image
        center = np.uint8(center)
        
        count = [0,0,0,0,0,0]
        
        for j in range(K):
            count[j] = np.count_nonzero(label == j)

        max_value = max(count)
        max_index = count.index(max_value)
        print(center[max_index])

       
        
        # Zapisuje ramke R
        center[max_index,2] = 1.2*center[max_index,2]
        if (center[max_index,2] >255):
            center[max_index,2] = 255

        if (center[max_index,2] < 10):
            bufR = "R00%i" % center[max_index,2]
    
        if ((center[max_index,2] >= 10) and (center[max_index,2] < 100)):
            bufR = "R0%i" % center[max_index,2]
    
        if (center[max_index,2] >= 100):
            bufR = "R%i" % center[max_index,2]
        # Zapisuje ramke G
        center[max_index,1] = 0.7*center[max_index,1]
        if (center[max_index,1] < 10):
            bufG = "G00%i" % center[max_index,1]
    
        if ((center[max_index,1] >= 10) and (center[max_index,1] < 100)):
            bufG = "G0%i" % center[max_index,1]
    
        if (center[max_index,1] >= 100):
            bufG = "G%i" % center[max_index,1]
        # Zapisuje ramke B
        center[max_index,0] = 0.7*center[max_index,0]
        if (center[max_index,0] < 10):
            bufB = "B00%i\r\n" % center[max_index,0]
    
        if ((center[max_index,0] >= 10) and (center[max_index,0] < 100)):
            bufB = "B0%i\r\n" % center[max_index,0]
    
        if (center[max_index,0] >= 100):
            bufB = "B%i\r\n" % center[max_index,0]

        print(bufR,bufG,bufB)
        ser = serial.Serial('/dev/rfcomm0')  # open serial port
        ser.write(bytes(bufR,'utf-8'))
        ser.write(bytes(bufG,'utf-8'))
        ser.write(bytes(bufB,'utf-8'))
        ser.close()  
    
        # Finally, reset the stream for the next capture
        # Jest szansa mieć szanse
        stream.seek(0)
        stream.truncate()
        

y1 = 60
y2 = 270
x1 = 40
x2 = 480
with picamera.PiCamera() as camera:
    
    camera.resolution = (640, 360)
    camera.framerate = 10
    time.sleep(2)
    for k in range(3600):
        start = time.time()
        camera.capture_sequence(outputs(), 'jpeg',use_video_port=True)
        finish = time.time()
        print('Captured 6 images at %.2ffps' % (6 / (finish - start)))


