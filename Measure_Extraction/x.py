import math
import numpy as np

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
    line_value = np.array([-1, -1, -1, -1])
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

def time_for_trapezoid(initial_s, final_s, acceleration, time, distance):
    a = 1/(acceleration)
    b = time + (initial_s+final_s)/acceleration
    c = -1 * (distance + (initial_s**2+final_s**2)/(2*acceleration))
    answer = quadratic(a, b, c)
    return answer
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
    
# Magnitude of vector
def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

# Normalize vector to unit vector
def normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0: 
       return vector
    return vector / norm

# Returns list of changes in position for each frame. One dimension at a time
def get_position_increments(initial_s, final_s, max_s, acceleration, time, fps, displacement):
    # Kind of get that velocity graph, and move through it.
    position_list = []
    time_step = 1/fps
    time_to_accelerate = (max_s-initial_s)/acceleration
    time_to_decelerate = abs((max_s-final_s)/acceleration)
    extra_time = 0
    if(time_to_accelerate+time_to_decelerate < time):
        distance_covered = time_to_accelerate*(initial_s+0.5*(max_s-initial_s))+time_to_decelerate*(final_s+0.5*(abs(max_s-final_s)))
        extra_time = (displacement-distance_covered)/max_s
    if(time_to_accelerate+time_to_decelerate > time):
        time_to_accelerate = time_for_V(acceleration, initial_s, final_s, displacement)
        time_to_decelerate = time_to_accelerate + (initial_s - final_s)/acceleration 
    time = time_step
    while(time <= time_to_accelerate):
        time += time_step
        position_list.append(initial_s*time + 0.5*acceleration*time**2)
    time = time_step
    initial_x = position_list[len(position_list)-1]
    while(time < extra_time):
        time += time_step
        position_list.append(initial_x + max_s*time)
    time = time_step
    initial_x = position_list[len(position_list)-1]
    while(time <= time_to_decelerate):
        time += time_step
        position_list.append(initial_x+max_s*time-0.5*acceleration*time**2)
    if(displacement < 0):
        position_list = [i * -1 for i in position_list]
    change_in_position = [position_list[0]]
    for i in range(1, len(position_list)):
        change_in_position.append(position_list[i]-position_list[i-1])
    return change_in_position 

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
    curr_line = x[0]
    
    max_bed_velocity = np.array([0, 0, 0])
    max_speed = 0
    bed_position = [float(bed[0]), float(bed[1]), float(bed[1])]
    bed_velocity = np.array([0, 0, 0])
    bed_velocity_magnitude = 0 # mm/s

    while(True): # Loop until end of gcode
        if(g_index == -1): break
        x = next_relevant_line(data, g_index)
        g_index = x[1]
        next_line = x[0]
        
        if(curr_line[3] != -1):
            max_speed = curr_line[3] / 60 # mm/s
        
        position_vector = curr_line[0:3] - bed
        max_bed_velocity = normalize(position_vector) * max_speed
        
        next_max_speed = max_speed
        if(next_line[3] != -1): next_max_speed = next_line[3]
        next_max_bed_velocity = normalize(next_line[0:3] - curr_line[0:3]) * next_max_speed
        
        final_bed_velociy = [max_bed_velocity]
        for i in range(3):
            if(final_bed_velociy[i] > next_max_bed_velocity[i]): final_bed_velociy[i] = next_max_bed_velocity[i]
            
        vector_times = np.array([0,0,0]) # Time it would take each vector to move given distance
        if(curr_line[0] != -1):
            vector_times[0] = time_to_move(abs(bed_position[0]-curr_line[0]),bed_velocity[0], final_bed_velociy[0], [max_bed_velocity[0], maxA[0]])
        if(curr_line[1] != -1):
            vector_times[1] = time_to_move(abs(bed_position[1]-curr_line[1]),bed_velocity[1], final_bed_velociy[1], [max_bed_velocity[1], maxA[1]])
        if(curr_line[2] != -1):
            vector_times[2] = time_to_move(abs(bed_position[2]-curr_line[2]),bed_velocity[2], final_bed_velociy[2], [max_bed_velocity[0], maxA[2]])
        
        time = np.amax(vector_times)
        update_x = get_position_increments(bed_velocity[0], final_bed_velociy[0], max_bed_velocity[0], maxA[0], time, fps, abs(bed_position[0]-curr_line[0]))
        update_y = get_position_increments(bed_velocity[1], final_bed_velociy[1], max_bed_velocity[1], maxA[1], time, fps, abs(bed_position[1]-curr_line[1]))
        update_z = get_position_increments(bed_velocity[2], final_bed_velociy[2], max_bed_velocity[2], maxA[2], time, fps, abs(bed_position[0]-curr_line[2]))
        
        t = 0
        #while(t <= time):


        
        
                
    curr_line = next_line
    # (For end) We need to process that final line of gcode, stored in our curr_value
    return tip_frame

print(time_for_trapezoid(0, 20, 10, 10, 280))