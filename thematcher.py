# import the necessary packages
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import scipy
import json

# mse utility
def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

# loop through each file
for path, subdirs, files in os.walk('generated'):
    results = []
    
    for name in files:
        
        fileName = os.path.join(path, name)
        if (name == "spec-full.png"):
            target = cv2.imread(fileName) # with this image we loop through all the vault and find a match
            imgT = np.mean(target, axis=2)
            #print(name)
        else:
            continue
        
        
        print(path)

        # start
        for path2, subdirs2, files2 in os.walk('vault'):
            
            for name2 in files2:

                fileName2 = os.path.join(path2, name2)
                if (name2 == "spec-full.png"):
                    lookup_image = cv2.imread(fileName2)
                    imgS = np.mean(lookup_image, axis=2)
                    #print(name2)
                else:
                    continue
                
                #print("comparing: ", fileName, " with: ", fileName2)

                if (imgS.shape == imgT.shape):
                    # compute the mean squared error and structural similarity
                    # index for the images
                    m = mse(imgS, imgT)
                    s = ssim(imgS, imgT)

                    results.append([s, fileName2])

        if (results):
            
            sortedResults = sorted(results, reverse=True)

            print("match at: ", sortedResults[0]) # this is the match!!!

            print(sortedResults[0])

            # now load the data in the vault for the match of that time
            folderLookup = sortedResults[0][1].split('\\')[1]

            print("lookup", folderLookup)
            
            #print(folderLookup)
            filePath ="c:/Users/ladyvox/Documents/_lightlike/" + "vault" + "/" + folderLookup + "/" + "data.json" 
            f = open(filePath,)
            data = json.load(f)
            generatedType = data['type']
            generatedValue = data['value']
            print("generatedType: ", generatedType, " value: ", generatedValue)
            f.close()

            # now write the match
            try:
                folderLookupOg = fileName.split('\\')[1]

                jsonDump = {}
                jsonDump["time"] = folderLookupOg
                jsonDump["type"] = generatedType
                jsonDump["value"] = generatedValue

                print(jsonDump)
                
                filePathGen ="c:/Users/ladyvox/Documents/_lightlike/" + "generated" + "/" + folderLookupOg + "/" + "data.json" 
                    
                print(filePathGen)

                jsonFile = open(filePathGen, 'w' )
                json.dump(jsonDump, jsonFile)
                jsonFile.close()

            except:
                print("failed to write data")