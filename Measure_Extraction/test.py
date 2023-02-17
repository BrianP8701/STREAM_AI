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
def time_to_accelerate(acceleration, initial_s, final_s, distance):
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




