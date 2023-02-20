import math

def quadratic( a, b, c): 
    dis = b * b - 4 * a * c 
    sqrt_val = math.sqrt(abs(dis)) 
    if dis > 0: 
        return[(-b + sqrt_val)/(2 * a), (-b - sqrt_val)/(2 * a)]
    elif dis == 0: 
        return [(-b / (2 * a))]
    else:
        return [-1]

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

# Returns next line with movement, [X, Y, Z, F] including any speed changes, along with what line in gcode we are at
def next_relevant_line(data: list, index):
    line_value = [-1, -1, -1, -1]
    while(True):
        if(index == -1): break
        new_line = read_gline(data[index])
        index = getNextLine(data, index)
        if(new_line[3] != -1):
            line_value[3] = new_line[3]
        if(new_line[0] != -1 or new_line[1] != -1 or new_line[2] != -1):
            line_value[0] = new_line[0]
            line_value[1] = new_line[1]
            line_value[2] = new_line[2]
            return [line_value, index]
    return -1

# Given acceleration, distance, initial and final speed, how long to accelerate. Only V shape
def time_for_V(acceleration, initial_s, final_s, distance):
    a = acceleration
    b = 2*initial_s
    c = ((initial_s**2)-(final_s**2))/(2*acceleration) - distance
    answer = quadratic(a, b, c)
    if(answer[0] == -1): return -1
    if(len(answer) == 1): return answer[0]
    if(answer[1] > answer[0]):
        if(answer[0] > 0): return answer[0]
        return answer[1]
    if(answer[1] > 0): return answer[1]
    return answer[0]

# Returns fastest time to move given speeds and acceleration in one axis
def time_to_move(distance, initial_s, final_s, max_s, acceleration):
    time_to_accelerate = (max_s-initial_s)/acceleration
    time_to_decelerate = abs((max_s-final_s)/acceleration)
    distance_covered = time_to_accelerate*(initial_s+0.5*(max_s-initial_s))+time_to_decelerate*(final_s+0.5*(abs(max_s-final_s)))
    if(distance_covered == distance):
        
        return time_to_accelerate+time_to_decelerate
    elif(distance_covered < distance):
        extra_time = (distance-distance_covered)/max_s
        return time_to_accelerate+time_to_decelerate+extra_time
    else:
        time_to_accelerate = time_for_V(acceleration, initial_s, final_s, distance)
        time_to_decelerate = time_to_accelerate + (initial_s - final_s)/acceleration
        return time_to_accelerate+time_to_decelerate

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
    tip_box = [sX-6, sY-6, sX+5, sY+5] # Tip bounding box
    tip_frame = [] # List of bounding boxes for each frame
    tip_frame.append(tip_box)
    
    with open(g_path, 'r') as f_gcode:
        data = f_gcode.read()
        data: list = data.split("\n")
    
    x = next_relevant_line(data, 0) # X, Y, Z, F
    g_index = x[1]
    curr_val = x[0]
    
    current_speed = 0 # mm/s
    speed_goal = 0
    bed_position = [float(bed[0]), float(bed[1]), float(bed[1])]
    velocity = [0, 0, 0]

    while(True): # Loop until end of gcode
        
        x = next_relevant_line(data, g_index)
        g_index = x[1]
        future_val = x[0]
        
        if(curr_val[3] != -1):
            speed_goal = curr_val[3]
        if(curr_val[0] != -1 or curr_val[1] != -1 or curr_val[2] != -1):
            
            
            
            # We need to loop until we reach our destination. We don't know how many frames in advance                                                          
            
            # But wait!!! We need to check the next line to see if we have to decelerate. Oh boi that aint good
            
            # Next create method given all speeds, distance and time return a list of xyz positions. 
            
                
            curr_val = future_val
    # (For end) We need to process that final line of gcode, stored in our curr_value
    return tip_frame

