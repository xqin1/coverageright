#!C:\Python26\ArcGIS10.0\python.exe
# -*- coding: utf-8 -*-
import arcpy
import sys
import os
import subprocess
import json
 
def main():
	try:
		finalList = []
		rootDir = "C:\\projects\\Data\\americaroamer\\2012 Oct\\CoverageRight_SHP_201210\\Carriers"
		techCount = 0
		companyCount = 0
		for techType in os.listdir(rootDir):
		    tech={}
		    tech["techType"]=techType
		    techTypeDir = rootDir + "\\" + techType
		    finalList.append(tech)
		    finalList[techCount]["property"]=[]
		    techCount += 1

		    for company in os.listdir(techTypeDir):
		    	print techType + " " + company
		    	companyCount +=1
		    	companyObj={}
		    	companyObj["id"]=companyCount
		    	companyObj["companyName"]=company
		    	finalList[techCount-1]["property"].append(companyObj)
		    	shapeFileDir = techTypeDir + "\\" + company + "\\SHP"
		    	for shapeFile in os.listdir(shapeFileDir):
					if shapeFile.endswith("shp") and shapeFile.find('_ogr')==-1 :
						companyObj["fileName"]=shapeFile						
						if companyCount>396:
							print "dissolving " + shapeFile + " to " + shapeFile.split(".")[0] + "_dissolved.shp"	
							inFeature = shapeFileDir + "\\" + shapeFile
							outFeature = shapeFileDir + "\\" + shapeFile.split(".")[0] + "_dissolved.shp" 
							arcpy.Dissolve_management(inFeature,outFeature)
								
		print finalList
		jsondata = json.dumps(finalList, indent=4, skipkeys=True, sort_keys=True)
		with open("c:\\projects\\python\\coverageRigh201210_dissolved.json" , 'w') as f:
			f.write(jsondata)
		f.closed
	except: 
		print "Error:", sys.exc_info()[0]   
		raise
		sys.exit(1)   
	finally:   
		print "finished"
 
if __name__ == "__main__":
	main()