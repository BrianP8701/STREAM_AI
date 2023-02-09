import cv2
import numpy as np
import gParser as gp
import time

def draw_rectangle(image_path, x, y, a, b):
    image = cv2.imread(image_path)
    
    cv2.rectangle(image, (x, y), (a, b), (255, 0, 0), 1)
    cv2.imshow('', image)
    cv2.waitKey(3000)
    
def measure_diameter(video_path, g_code):
    cam = cv2.VideoCapture(video_path)
    
    currentframe = 0
    currentTime = 0 # Remember to divide time by 3
    g_line = 0
    
    bounding_boxes = gp.interpret(g_code, 30, 10.45212638, 657, 697, 82.554, 82.099, 1.8)
        
    while(True):
        ret,frame = cam.read()
        frame = np.dot(frame[...,:3], [0.299, 0.587, 0.114])
        
        draw_rectangle("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/data/frame" + str(currentframe) + ".jpg", bounding_boxes[currentframe][0], bounding_boxes[currentframe][1], bounding_boxes[currentframe][2], bounding_boxes[currentframe][3])
        #time.sleep(3)
        print(bounding_boxes[currentframe])
        if ret:
            # if video is still left continue creating images
            name = './data/frame' + str(currentframe) + '.jpg'
            
        
            cv2.imwrite(name, frame)
            currentframe += 1
        else:
            break
  
    cam.release()
    cv2.destroyAllWindows()







bounding_boxes = gp.interpret("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/gcode1.gcode", 30, 15.99233361, 427, 403, 82.554, 82.099, 1.8)
currentframe = 4000
draw_rectangle("/Users/brianprzezdziecki/Research/Mechatronics/Anomaly_Detection/data/frame" + str(currentframe) + ".jpg", bounding_boxes[currentframe][0], bounding_boxes[currentframe][1], bounding_boxes[currentframe][2], bounding_boxes[currentframe][3])
#print(bounding_boxes[:20])

#draw_rectangle("/Users/brianprzezdziecki/Research/Mechatronics/Anomaly_Detection/data/frame0.jpg", 424, 400, 429, 405)
