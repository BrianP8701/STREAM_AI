import math
#   F    -   Represents the speed(mm/min) of movement of extruder
#   E    -   Cumulative amount of material that's been extruded so far
#   G92  -   Set values to ____ 

# Returns index of next line beginning with 'G1'
def getNextLine(data: list, index) -> int:
    index += 1
    while(index < len(data)):
        if(data[index][:2] == 'G1'): return index
        index += 1
    return -1


#   Returns [X, Y, Z, F] from a line of gcode. -1 if NA
def read_gline(line: str) -> list:
    val = [-1, -1, -1, -1]
    try:
        index_value = line.index(';')
        line = line[:index_value]
    except ValueError:
        index_value = -1
    line: list = line.split(" ")
    
    for c in line:
        if(c[:1] == "X"): val[0] = c[1:]
        elif(c[:1] == "Y"): val[1] = c[1:]
        elif(c[:1] == "Z"): val[2] = c[1:]
        elif(c[:1] == "F"): val[3] = c[1:]
    return val

#   Euclidean distance
def distance(x, y, z, a, b, c):
    return math.sqrt((x - a)**2 + (y - b)**2 + (z - c)**2)

#   
def x_v(x, y, a, b, v):
    if x-a == 0: return 0
    theta = math.atan(abs(y-b)/abs(x-a))
    return v * math.cos(theta)

# Arguments:
#   g_path  -  Pathname of .gcode file
#   fps     -  FPS of video
#   mTp     -  Initial ratio of 1 millimeter to pixels
#   sX      -  Initial X coordinate on image
#   sY      -  Y coordinate on image
#   bed     -  [x, y, z] Initial bed coordinates
#   maxA    -  [x, y, z] Max accelerations in each axis
# Returns a list containing the bounding boxes for tip of extruder
def interpret(g_path, fps, mTp, sX, sY, bed, maxA):
    tip_box = [sX-3, sY-3, sX+2, sY+2] # Tip bounding box
    tip_frame = [] # List of bounding boxes for each frame
    tip_frame.append(tip_box)
    
    with open(g_path, 'r') as f_gcode:
        data = f_gcode.read()
        data: list = data.split("\n")
    
    g_index = -1 # Line in gcode
    current_speed = 0 # mm/s
    position = [float(bed[0]), float(bed[1]), float(bed[1])]
    velocity = [0, 0, 0]
    acceleration = [maxA[0], maxA[1], maxA[2]]
    
    while(True): # Loop until end of gcode
        g_index = getNextLine(data, g_index)
        if(g_index == -1): break
        gline = data[g_index]
    
        curr_val = read_gline(gline) # X, Y, Z, F
        
        if curr_val[3] != -1:
            current_speed = float(curr_val[3]) / 60
        if curr_val[0] != -1 or curr_val[1] != -1 or curr_val[2] != -1:
            prevX = x
            prevY = y
            prevZ = z
            if(curr_val[0] == -1): x = prevX
            else: x = float(curr_val[0])
            if(curr_val[1] == -1): y = prevY
            else: y = float(curr_val[1])
            if(curr_val[2] == -1): z = prevZ
            else: z = float(curr_val[2])
    
            dist = distance(prevX, prevY, prevZ, x, y, z) # mm
            
            move_time = dist / current_speed # Time to complete this line of gcode (seconds)
            move_frames = int(move_time * fps) # Frames in this line
            x_velocity = x_v(prevX, prevY, x, y, current_speed) # Speed of extruder in x direction
            pixels_a_frame = abs((x_velocity*mTp) / fps) # Try with and without abs
            if prevX > x: pixels_a_frame *= -1 
            
            # z_velocity  # This will change mTp, and move in the y direction. It will also have a horizontal effect
            
            # Iterating through frames for this line of gcode
            for i in range(move_frames-1):
                sX += pixels_a_frame
                tip_box = [int(sX)-3, sY-3, int(sX)+2, sY+2]
                tip_frame.append(tip_box)
            
            # Let's get how many frames we need to move and change in x every frame
    return tip_frame
            
def crop(g_path, fps, mTp, tip: list, prevX, prevY, prevZ):
    x = prevX
    y = prevY
    z = prevZ
    with open(g_path, 'r') as f_gcode:
        data = f_gcode.read()
        data: list = data.split("\n")
    
    g_index = -1 # Line in gcode
    current_speed = 0 # mm/s
    frame = 0
    
    bounding_boxes = []
    temporary_tracker = []
    
    while(True): # Loop until end of gcode
        g_index = getNextLine(data, g_index)
        if(g_index == -1): break
        gline = data[g_index]
    
        curr_val = read_gline(gline) # X, Y, Z, F
        
        if curr_val[3] != -1:
            current_speed = float(curr_val[3]) / 60
        if curr_val[0] != -1 or curr_val[1] != -1 or curr_val[2] != -1:
            prevX = x
            prevY = y
            prevZ = z
            if(curr_val[0] == -1): x = prevX
            else: x = float(curr_val[0])
            if(curr_val[1] == -1): y = prevY
            else: y = float(curr_val[1])
            if(curr_val[2] == -1): z = prevZ
            else: z = float(curr_val[2])
        
            dist = distance(prevX, prevY, prevZ, x, y, z)
            
            # Next bed destination: x, y
            # Previous pos on bed: prevX, prevY
            # Current tip coords: tip[frame][0], tip[frame][1]
            
            move_time = dist / current_speed # Time to complete this line of gcode (seconds)
            move_frames = int(move_time * fps) # Frames in this line
            
            L = (current_speed / mTp) * 60 # Distance in pixels to move back from tip to crop
            theta = 0
            if(x-prevX != 0 ): theta = (math.atan(abs(y-prevY)/abs(x-prevX)) * (180 / math.pi))**2 / 90 # Angle to crop torwards in image
            dx = L * math.cos(theta * (math.pi / 180))
            dy = L * math.sin(theta * (math.pi / 180))
            
            temp = [L, theta, dx, dy]
            
            for i in range(move_frames-1):
                if(frame == len(tip)-1): break
                cropY = tip[frame][1]
                cropX = tip[frame][0]
                A = tip[frame][0]
                B = tip[frame][1]
            
                if(y > prevY): cropY += dy
                else: cropY -= dy
                if(x > prevX): cropX -= dx
                else: cropX += dx
                
                if(theta > 85): # Moving vertically
                    if(A > cropX): 
                        A += 8
                        cropX -= 8
                    else:
                        A -= 8
                        cropX += 8
                elif(theta < 5):
                    if(B > cropY): 
                        B += 8
                        cropY -= 8
                    else:
                        B -= 8
                        cropY += 8
                #elif()
                
                temporary_tracker.append(temp)
                if(tip[frame][0] == -1): bounding_boxes.append([0,0,0,0])
                else: bounding_boxes.append([int(cropX), int(cropY), int(A), int(B)])
                frame += 1
    return [bounding_boxes, temporary_tracker]
        
            
           
        
#bounding_boxes = interpret("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/gcode1.gcode", 30, 10.45212638, 657, 697, 82.554, 82.099, 1.8)


