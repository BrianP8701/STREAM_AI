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

# Arguments:
#   line   -  A line of gcode
# Returns: 
#   [X, Y, Z, F] - The corresponding values, -1 if empty
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

def distance(x, y, z, a, b, c):
    return math.sqrt((x - a)**2 + (y - b)**2 + (z - c)**2)

def x_v(x, y, a, b, v):
    if x-a == 0: return 0
    theta = math.atan(abs(y-b)/abs(x-a))
    return v * math.cos(theta)

# Arguments:
#   g_path  -  Pathname of .gcode file
#   fps     -  FPS of video
#   mTp     -  Ratio of 1 millisecond to pixels
#   sX      -  Initial X coordinate on image
#   Y       -  Y coordinate on image
#   tempX   -  Initial x coordinate on bed
#   tempY   -  Initial y coordinate on bed
#   tempZ   -  Initial z coordinate on bed
# Returns:
#   A list containing the bounding boxes for tip of extruder
def interpret(g_path, fps, mTp, sX, Y, tempX, tempY, tempZ):
    tip_box = [sX-3, Y-3, sX+2, Y+2] # Tip bounding box
    x = float(tempX)
    y = float(tempY)
    z = float(tempZ)
    tip_frame = [] # List of bounding boxes for each frame
    tip_frame.append(tip_box)
    
    with open(g_path, 'r') as f_gcode:
        data = f_gcode.read()
        data: list = data.split("\n")
    
    g_index = -1 # Line in gcode
    current_speed = 0 # mm/s
    
    while(True): # Loop until end of gcode
        g_index = getNextLine(data, g_index)
        if(g_index == -1): break
        gline = data[g_index]
    
        curr_val = read_gline(gline) # X, Y, Z, F
        
        if curr_val[3] != -1:
            current_speed = float(curr_val[3]) / 60
        if curr_val[0] != -1 or curr_val[1] != -1 or curr_val[2] != -1:
            # I'll have to calculate:
        #   Angle to crop
        #   Next destination coordinate
        #   Iteratively add to tip frame
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
            
            move_time = dist / current_speed # Time to complete this line of gcode (seconds)
            move_frames = int(move_time * fps) # Frames in this line
            x_velocity = x_v(prevX, prevY, x, y, current_speed) # Speed of extruder in x direction
            pixels_a_frame = abs((x_velocity*mTp) / fps) # Try with and without abs
            if prevX > x: pixels_a_frame *= -1 
            
            # Iterating through frames for this line of gcode
            for i in range(move_frames-1):
                sX += pixels_a_frame
                tip_box = [int(sX)-3, Y-3, int(sX)+2, Y+2]
                tip_frame.append(tip_box)
            
            # Let's get how many frames we need to move and change in x every frame
    return tip_frame
            
            
            
           
        
#bounding_boxes = interpret("/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/gcode1.gcode", 30, 10.45212638, 657, 697, 82.554, 82.099, 1.8)


