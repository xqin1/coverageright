#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
import psycopg2
#note that we have to import the Psycopg2 extras library!
import psycopg2.extras
import sys
import os
import subprocess
import json
 
def main():
	try:
		finalList = []
		rootDir = "C:\\projects\\Data\\americaroamer\\2012 Oct\\CoverageRight_SHP_201210\\Carriers"
		#conn_string = "host='165.135.239.38' dbname='gisdb' user='bbmap' password='bbmap_ps'"	
		host = "165.135.239.38"
		dbname = "gisdb" 
		schema = "swat"
		tableName = "coverageright201210_montana"
		user = "bbmap"
		password = "bbmap_ps"
		conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"	 

		conn = psycopg2.connect(conn_string)
		cursor = conn.cursor()
		techCount = 0
		companyCount = 0
		sqlComm = "DROP TABLE IF EXISTS " + schema + "." + tableName + " CASCADE"
		cursor.execute(sqlComm)
		conn.commit()
		sqlComm = "CREATE TABLE " + schema + "." + tableName + " (gid integer PRIMARY KEY,entity varchar(100), protocol varchar(100))"
		cursor.execute(sqlComm)
		conn.commit()
		sqlComm = "SELECT AddGeometryColumn('" + schema + "','" + tableName + "', 'geom', 4326, 'MULTIPOLYGON', 2 )"

		cursor.execute(sqlComm)
		conn.commit()
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
					if shapeFile.endswith("shp") and shapeFile.find('montana')>0:
						companyObj["fileName"]=shapeFile
						# p = subprocess.Popen('ogrinfo -al -so "' + shapeFileDir + "\\" + shapeFile + '"', stdout=subprocess.PIPE)
						# for line in p.stdout:
						# 	if line.find('Extent') != -1:
						# 		extent = line.replace(")", "").replace("- (", ",").replace(" ", "").replace("(", "").replace("Extent:","").split(",")
						# 		ext = []
						# 		for e in extent:
						# 			ext.append(float(e))
						# 		companyObj["extent"]=ext
						# p.wait()
						if companyCount>0:
							print companyCount
							shpComm = 'shp2pgsql -s 4326 -d -I -W latin1 -g geom "' + shapeFileDir + "\\" + shapeFile + '" ' + schema + "." + shapeFile.replace("_dissolved_montana.shp","") + " | psql -h " + host + " -d " + dbname + " -U " + user
							print "load " + shapeFile + " to postgres"
							shpP = subprocess.call(shpComm,shell=True)
							sqlComm = "insert into " + schema + "." + tableName + " select " + str(companyCount) + ", '" + company + "','" + techType + "', geom from " +  schema + "." + shapeFile.replace("_dissolved_montana.shp","")
							print sqlComm
							cursor.execute(sqlComm)
							conn.commit()
							sqlComm = "drop table if EXISTS " + schema + "." + shapeFile.replace("_dissolved_montana.shp","") + " CASCADE"
							cursor.execute(sqlComm)
							conn.commit()		
		print finalList
		# sqlComm  = "CREATE INDEX " + tableName + "_geom_gist ON " + schema + "." + tableName + " USING gist (geom )"
		# cursor.execute(sqlComm)
		# conn.commit()
		jsondata = json.dumps(finalList, indent=4, skipkeys=True, sort_keys=True)
		with open("c:\\projects\\python\\coverageRigh201210_dev_montana.json" , 'w') as f:
			f.write(jsondata)
		f.closed

	except psycopg2.DatabaseError, e: 
		if conn:
			conn.rollback() 
		print 'Error %s' % e    
		sys.exit(1)   
	finally:   
		if conn:
			conn.close()
 
if __name__ == "__main__":
	main()