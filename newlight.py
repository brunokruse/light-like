import librosa
import librosa.display
import librosa.feature

import matplotlib.pyplot as plt

import soundfile as sf
import numpy as np
import skimage.io

import math
import json
import os
from datetime import datetime
import time


# if song has .json
# inputs: .ogg, .json

# if song does not have json
# inputs: .ogg, ==> analyze

# analyization
# dual spectrograph
# vocals, percussion

# ^ with this above data match with the 
# data map (hollaback girl)

# todo: move these globals to classes
global AUDIO_DATA, SAMPLE_RATE, TIMES_ARRAY, LPB, JSON_TIMES_ARRAY
AUDIO_DATA = None # empty until we load the audio
SAMPLE_RATE = 22050

TIMES_ARRAY = []
JSON_TIMES_ARRAY = [[],[],[]] 
LPB = 0

# utility
def beatToSeconds(inBeat):
    global LPB

    # 2.0 is the silence offest in the beginning
    # we multiply by 4 here to accomdate for the fact we want more resolution
    # in the beatstep later
    return round((2.0 * LPB) + (float(inBeat) * ( LPB  * 4) ), 4)  

def secondsToBeat(inSeconds, lpb):
    return (inSeconds/lpb)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

# json
def loadJson(inPath):
    global LPB
    global JSON_TIMES_ARRAY
    global TIMES_ARRAY

    f = open(inPath,)
    data = json.load(f)

    for i in data['events']:
        print(beatToSeconds(i['time']))

        JSON_TIMES_ARRAY[0].append( beatToSeconds(i['time'] ) )
        JSON_TIMES_ARRAY[1].append( i['type']  )
        JSON_TIMES_ARRAY[2].append( i['value'] )

    f.close()

    # find the closest match and map the new time array to the
    # original lightmap data. the idea here is to establish some
    # consistancy across files and timings
    for t in TIMES_ARRAY:
        result = find_nearest(JSON_TIMES_ARRAY[0], t) # this is the match

        index = JSON_TIMES_ARRAY[0].index(result)

        # finally this is the new data. we use this as an answer key for lookups
        print("time: ", result, "type: " , JSON_TIMES_ARRAY[1][index], " value: ", JSON_TIMES_ARRAY[2][index])

        jsonDump = {
            "time: " : result,
            "type: " : JSON_TIMES_ARRAY[1][index],
            "value: " : JSON_TIMES_ARRAY[2][index]
        }

        try:
            # write the data out here
            filePath = "vault\\" + str(t) + "\\" + "data.json"
            with open(filePath, 'x') as f:
                json.dump(jsonDump, f)
        except:
            print("failed to write data")

# song information for reference
class TrackData(object):
    def _init__(sef):
        print("init TrackData")

# beat data frame
class DataFrame(object):
    def __init__(self):
        print("init DataFrame")

# generate times
def generateTimesForTrack(inPath):
    global AUDIO_DATA # todo: to class ^^
    global SAMPLE_RATE
    global TIMES_ARRAY
    global LPB
    global JSON_TIMES_ARRAY
    global TIMES_ARRAY

    # calculate the number of time _events in the data,
    # we want to do this if we have a new song without
    # any time data

    # this information below should be moved
    # to a class
    #bpm = inBPM         # beats per minute
    y, sr = librosa.core.load(inPath, sr=22050)
    AUDIO_DATA = y
    SAMPLE_RATE = 22050
    
    # this beats array below works based on onset intervals
    # https://librosa.org/doc/main/generated/librosa.beat.beat_track.html
    bpm, beats = librosa.beat.beat_track(y=y, sr=sr)

    bps = bpm / 60  # beats per second
    durationSeconds = librosa.get_duration(y=y, sr=sr)
    durationMinutes = durationSeconds / 60  # for easier calculation
    totalBeats = int(bpm * durationMinutes)
    lpb = 1 / (bpm / 60) # length of time per beat

    beatStep = 4 # 4ths, 8ths, 16ths
    LPB = round(lpb / beatStep, 4)

    # debug flag
    print(
        "bpm: " + str(bpm), 
        "bps: " + str(bps),
        "durationSeconds: " + str(durationSeconds),
        "durationMinutes: " + str(durationMinutes), 
        "totalBeats: " + str(totalBeats), 
        "lengthPerBeat: " + str(lpb),
        "lengthPerEventNote LPB: " + str(LPB))

    # convert to timestamps
    beatTrack = librosa.frames_to_time(beats, sr=sr)

    #working
    # generate timestamps
    # 1,4,8,16X per beat, based on BPM
    timesArray = [] # populate this with the times
    for i in range(0, totalBeats * beatStep):

        calculatedBeatTime = beatToSeconds(i/4)

        #print(str(i), calculatedBeatTime)
        timesArray.append(calculatedBeatTime)

    # zero crossing
    #zcrs = librosa.feature.zero_crossing_rate(y)
    #zcrsTrack = librosa.frames_to_time(zcrs, sr=sr)
    #zero_crossings = librosa.zero_crossings (y, pad=False)
    #print(sum(zero_crossings))
    
    # at this point we have two time arrays, combine them
    # to have a full array of "time"
    # 1, calculated by the beat step
    # 2, analyzed by librosa onset envelopes
    # 3, ZCR ?
    # 4, option to add and remove time points in the analaysis

    # using naive method to concat 
    combinedTimesArray = []
    for time in timesArray:
        combinedTimesArray.append(round(time,4))
    for beatTime in beatTrack:
        combinedTimesArray.append(round(beatTime,4))

    combinedTimesArray.sort() # shuffle them in order
    TIMES_ARRAY = combinedTimesArray 

    # finally, our rough list of event times
    # print(combinedTimesArray)
    
    # debug
    print("total events: " + str(len(TIMES_ARRAY)))

    # preload json

    # preload False means we have no lightmap data
    # preload True means we have lightmap data and we are writing the json data/types as we go
    preload = False
    data = None
    if (preload):
        f = open('Easy.json',)
        data = json.load(f)

        for i in data['events']:
            print(beatToSeconds(i['time']))

            JSON_TIMES_ARRAY[0].append( beatToSeconds(i['time'] ) )
            JSON_TIMES_ARRAY[1].append( i['type']  )
            JSON_TIMES_ARRAY[2].append( i['value'] )

        f.close()

    print(TIMES_ARRAY)

    debug = False
    if debug is False:
        for time in TIMES_ARRAY:

            # data snippet
            try:
                timeStart = time
                timeEnd = timeStart + round(LPB, 4)
                print(int(timeStart), int(timeEnd))
                data = AUDIO_DATA[int(timeStart) * SAMPLE_RATE: int(timeEnd+1) * SAMPLE_RATE]

                print(data)

                D = librosa.stft(data)
                D_harmonic, D_percussive = librosa.decompose.hpss(D, margin=8)
                rp = np.max(np.abs(D))
                
                filePath = ""

                if(preload):
                    filePath = "vault\\" + str(time)
                else:
                    filePath = "generated\\" + str(time)

                try:
                    if not os.path.exists(filePath):
                        os.makedirs(filePath)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        print("filepath error")
                        raise
                
                print(filePath)
                
                # write audio data
                fileName = filePath + '\\' + "audio.wav"
                print(fileName)
                sf.write(fileName, data, SAMPLE_RATE, format='ogg', subtype='vorbis')
                print("successfully wrote audio!")

                # save each image in the spectrogram to file for later analysis
                # the full spectrogram image
                plt.figure(figsize=(3, 3))
                plt.axis('off')
                plt.tight_layout()
                librosa.display.specshow(librosa.amplitude_to_db(np.abs(D), ref=rp), y_axis='log', x_axis='time')
                fileName = filePath + '\\' + "spec-full.png"
                print(fileName)       
                plt.savefig(fileName)
                plt.close()
                
                # the harmonic image
                plt.figure(figsize=(3, 3))
                plt.axis('off')
                plt.tight_layout()
                librosa.display.specshow(librosa.amplitude_to_db(np.abs(D_harmonic), ref=rp),  y_axis='log', x_axis='time')
                fileName = filePath + '\\' + "spec-harmonic.png"
                print(fileName)
                plt.savefig(fileName)
                plt.close()

                # the percussive image
                plt.figure(figsize=(3, 3))
                plt.axis('off')
                plt.tight_layout()
                librosa.display.specshow(librosa.amplitude_to_db(np.abs(D_percussive), ref=rp), y_axis='log', x_axis='time')
                fileName = filePath + '\\' + "spec-percussive.png"
                print(fileName)
                plt.savefig(fileName)
                plt.close()

                print("images saved!")
                

                if (preload):
                    # now write the times
                    result = find_nearest(JSON_TIMES_ARRAY[0], time) # this is the match
                    print("result: ", result)

                    index = JSON_TIMES_ARRAY[0].index(result)
                    print("index: ", index)

                    # finally this is the new data. we use this as an answer key for lookups
                    print("time: ", result, "type: " , JSON_TIMES_ARRAY[1][index], " value: ", JSON_TIMES_ARRAY[2][index])

                    try:
                        jsonDump = {}
                        jsonDump["time"] = time
                        jsonDump["type"] = JSON_TIMES_ARRAY[1][index]
                        jsonDump["value"] = JSON_TIMES_ARRAY[2][index]

                        print(jsonDump)
                                        
                        fileName = filePath + "\\" + "data.json"
                        print(fileName)

                        jsonFile = open(fileName, 'w' )
                        json.dump(jsonDump, jsonFile)
                        jsonFile.close()

                    except:
                        print("failed to write data")
                    
            except:
                print("can't save images for this time: " + str(time))
                
def main():
    global AUDIO_DATA
    global TIMES_ARRAY


    

    #startTime = datetime.now()
    #current_time = startTime.strftime("%H:%M:%S")
    #print("Start Time =", current_time)
    #print("main")

    # if we have lightmapdata
    #loadJson('Easy.json')

    # if we dont have lightmapdata
    generateTimesForTrack('song.ogg')
    #loadJson('Easy.json')

    #endTime = datetime.now()
    #current_time = endTime.strftime("%H:%M:%S")
    #print("End Time =", current_time)

main()