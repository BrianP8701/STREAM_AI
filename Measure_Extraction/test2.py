import json
  
# Opening JSON file
f = open('/Users/brianprzezdziecki/Research/Mechatronics/STREAM_AI/Measure_Extraction/Video1.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
for i in data:
    print(type(i))
  
# Closing file
f.close()