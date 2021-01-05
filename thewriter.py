import numpy as np
import os
import scipy
import json

# utility
def secondsToBeat(inSeconds, lpb):
    return (inSeconds/lpb)

jsonDump = {}

jsonDump["_version"] = "0.0.0"
jsonDump["_BPMChanges"] = []
jsonDump["_events"] = []

# loop through each file
for path, subdirs, files in os.walk('generated+data'):
    
    results = []
    
    sorted(files)

    for name in files:
        
        if (name == "data.json"):
            print("-")
            folderLookup = path.split('\\')[1] # gets the beat number
            fileName = os.path.join(path, name)
            filePath ="c:/Users/ladyvox/Documents/_lightlike" + "/generated+data/" + folderLookup + "/" + "data.json" 

            f = open(filePath,)
            data = json.load(f)
            f.close()
            
            inTime = data['time']
            convertedTimeToBeat = secondsToBeat(float(data['time']), 0.1335 * 4) # every quarter beat
            inType = data['type']
            inValue = data['value']

            print ( str(inTime), str(convertedTimeToBeat), str(inType), str(inValue) )
            frameObj = {
                "_time": str(convertedTimeToBeat),
                "_type": str(inType),
                "_value": str(inValue)
                }

            jsonDump["_events"].append(frameObj)

    

print (jsonDump)
try:
    # write the data out here
    filePath = "final\\" + "Easy.dat"
    with open(filePath, 'x') as f:
        json.dump(jsonDump, f)
except:
    print("failed to write data")