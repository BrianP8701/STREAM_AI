import cv2
import numpy as np
import gParser as gp
import time
import json

def draw_rectangle(image_path, x, y, a, b):
    image = cv2.imread(image_path)
        
    cv2.rectangle(image, (x, y), (a, b), (255, 0, 0), 1)
    cv2.imshow('', image)
    cv2.waitKey(10000)
    
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


def measure_diameter2(video_path, json_path, g_code):
    cam = cv2.VideoCapture(video_path)
    
    tip = []
    f = open(json_path)
    data = json.load(f)
    for i in data:
        tip.append([i.get('x'), i.get('y')])
    f.close()
    
    bounding_boxes = gp.crop(g_code, 30, 17.82233361, tip, 82.554, 82.099, 1.8)
    
    
    
    currentframe = 0
    currentTime = 0 # Remember to divide time by 3
    g_line = 0




bounding_boxes = gp.interpret("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/gcode1.gcode", 30, 15.99233361, 427, 403, 82.554, 82.099, 1.8)
print(len(bounding_boxes))
currentframe = 50

#tip = []
#f = open('/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/Measure_Extraction/Video1.json')
#data = json.load(f)
#for i in data:
    #tip.append([i.get('x'), i.get('y')])
#f.close()
#bounding_boxes = gp.crop("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/gcode1.gcode", 30, 17.82233361, tip, 82.554, 82.099, 1.8)[0]
#tracker =  gp.crop("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/gcode1.gcode", 30, 17.82233361, tip, 82.554, 82.099, 1.8)[1]
#currentframe = 20
#print(len(bounding_boxes))
#print("x " +str(bounding_boxes[0][0]))
#print('y ' + str(bounding_boxes[0][1]))
#print('L ' + str(tracker[0][0]))
#print('theta ' + str(tracker[0][1]))
#print('dx ' + str(tracker[0][2]))
#print('dy ' + str(tracker[0][3]))
#print()
#print("x " +str(bounding_boxes[20][0]))
#print('y ' + str(bounding_boxes[20][1]))
#print('L ' + str(tracker[20][0]))
#print('theta ' + str(tracker[20][1]))
#print('dx ' + str(tracker[20][2]))
#print('dy ' + str(tracker[20][3]))

draw_rectangle("/Users/brianprzezdziecki/Research/Mechatronics/data/frame" + str(currentframe) + ".jpg", bounding_boxes[currentframe][0], bounding_boxes[currentframe][1], bounding_boxes[currentframe][2], bounding_boxes[currentframe][3])
#print(bounding_boxes[:20])

#draw_rectangle("/Users/brianprzezdziecki/Research/Mechatronics/Anomaly_Detection/data/frame0.jpg", 424, 400, 429, 405)
