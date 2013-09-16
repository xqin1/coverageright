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
		rootDir = "C:\\projects\\Data\\americaroamer\\2013 July\\Carriers"
		#conn_string = "host='165.135.239.38' dbname='gisdb' user='bbmap' password='bbmap_ps'"	
		# host = "localhost"
		# dbname = "gisdb20" 
		# schema = "swat"
		# tableName = "coverageright201210"
		# user = "postgres"
		# password = "xiali19690326!A"
		# conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"	 

		# conn = psycopg2.connect(conn_string)
		# cursor = conn.cursor()
		username = "admin";
		password = "geoserver";
		service = "http://165.135.239.37:8010/geoserver/rest/workspaces/" # geoserver URL
		serverPath = "/GEOWEB/data/americaroamer/coverageright201301/Carriers/"
		workspace = "coverageright201301"
		techCount = 0
		companyCount = 0
		# sqlComm = "DROP TABLE IF EXISTS " + schema + "." + tableName + " CASCADE"
		# #cursor.execute("insert into swat.fixed_total_partial_unavail_5m select unavail_type,state_fips,ST_SimplifyPreserveTopology(geom,5) from swat.fixed_total_partial_unavail where state_fips=%(statefp)s", {'statefp':s})
		# cursor.execute(sqlComm)
		# conn.commit()
		# sqlComm = "CREATE TABLE " + schema + "." + tableName + " (gid integer PRIMARY KEY,entity varchar(100), protocol varchar(100))"
		# cursor.execute(sqlComm)
		# conn.commit()
		# sqlComm = "SELECT AddGeometryColumn('" + schema + "','" + tableName + "', 'geom', 4326, 'MULTIPOLYGON', 2 )"run
		# print sqlComm

		# cursor.execute(sqlComm)
		# conn.commit()
		# print sqlComm
		# 	print s + " done "
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
					if shapeFile.endswith("shp"):
						#companyObj["fileName"]=shapeFile
						companyObj["serviceName"]=shapeFile.split(".")[0]
						p = subprocess.Popen('ogrinfo -al -so "' + shapeFileDir + "\\" + shapeFile + '"', stdout=subprocess.PIPE)
						for line in p.stdout:
							if line.find('Extent') != -1:
								extent = line.replace(")", "").replace("- (", ",").replace(" ", "").replace("(", "").replace("Extent:","").split(",")
								ext = []
								for e in extent:
									ext.append(float(e))
								companyObj["extent"]=ext
						p.wait()

						curlComm = "curl -u " + username + ":" + password + ' -XPUT -H "Content-type: text/plain" -d "file:' + serverPath + techType +"/" + company + "/SHP/" + shapeFile + '"'
						curlComm = curlComm + " " + service + workspace +"/datastores/" + shapeFile.split(".")[0] + "/external.shp"
						print curlComm
						# print "load " + shapeFile + " to postgres"
						curlP = subprocess.call(curlComm,shell=True)
						# shpComm = 'shp2pgsql -s 4326 -d -I -W latin1 -g geom "' + shapeFileDir + "\\" + shapeFile + '" ' + schema + "." + shapeFile.split(".")[0] + " | psql -h " + host + " -d " + dbname + " -U " + user
						# #print shpComm
						# #shpP = subprocess.Popen(shpComm, stdout=None)
						# print "load " + shapeFile + " to postgres"
						# shpP = subprocess.call(shpComm,shell=True)
						# #os.system(shpComm)
						# sqlComm = "insert into " + schema + "." + tableName + " select " + str(companyCount) + ", '" + company + "','" + techType + "', st_multi(st_union(geom)) from " + schema + "." + shapeFile.split(".")[0] + " group by protocol"
						# print sqlComm
						# cursor.execute(sqlComm)
						# conn.commit()
						# sqlComm = "drop table if EXISTS " + schema + "." + shapeFile.split(".")[0] + " CASCADE"
						# cursor.execute(sqlComm)
						# conn.commit()		
		print finalList
		# sqlComm  = "CREATE INDEX " + tableName + "_geom_gist ON " + schema + "." + tableName + " USING gist (geom )"
		# cursor.execute(sqlComm)
		# conn.commit()
		jsondata = json.dumps(finalList, indent=4, skipkeys=True, sort_keys=True)
		with open("c:\\projects\\data\\americaroamer\\2013 July\\coverageRigh201307.json" , 'w') as f:
			f.write(jsondata)
		f.closed

	except psycopg2.DatabaseError, e: 
		# if conn:
		# 	conn.rollback() 
		print 'Error %s' % e    

		sys.exit(1)   
	finally:   
		# if conn:
		# 	conn.close()
		print "finished"
 
if __name__ == "__main__":
	main()