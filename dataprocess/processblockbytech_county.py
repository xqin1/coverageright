#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
import psycopg2
#note that we have to import the Psycopg2 extras library!
import psycopg2.extras
import sys
import os
import subprocess
import json
import time
 
def main():
	try:
		starttime = time.time()
		finalList = []
		rootDir = "C:\\projects\\Data\\americaroamer\\2013 Jan\\Carriers"
		#conn_string = "host='165.135.239.38' dbname='gisdb' user='bbmap' password='bbmap_ps'"	
		host = "localhost"
		dbname = "gisdb20" 
		schema = "swat"
		tableName = "coverageright201301LTEblock"
		user = "postgres"
		password = "xiali19690326!A"
		conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"	 

		conn = psycopg2.connect(conn_string)
		cursor = conn.cursor()

		# sqlComm = "DROP TABLE IF EXISTS " + schema + "." + tableName + " CASCADE"
		# cursor.execute(sqlComm)
		# conn.commit()
		# sqlComm = "CREATE TABLE " + schema + "." + tableName + " (entity varchar(100), protocol varchar(100), geoid10 varchar(15), ltepct double precision)"
		# cursor.execute(sqlComm)
		# conn.commit()
		statefp = ("01","02","04","05","06","08","09","10","11","12","13","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50","51","53","54","55","56","60","66","69","72","78")

		# cursor.execute(sqlComm)
		# conn.commit()
		companyCount = 0
		for techType in os.listdir(rootDir):
		    techTypeDir = rootDir + "\\" + techType
		    if techType == "LTE":
			    for company in os.listdir(techTypeDir):
			    	#print techType + " " + company
			    	shapeFileDir = techTypeDir + "\\" + company + "\\SHP"
			    	for shapeFile in os.listdir(shapeFileDir):
						if shapeFile.endswith("shp"):
							companyCount+=1
							if (companyCount > 16 and companyCount<19):
								print "calculate intersection states for company " + company
								sqlComm = "select distinct(statefp10) as statefp10 from census.state2010full_move a, swat.coverageright201301lte b " + \
										  "where b.entity = '" + company + "' and st_intersects(b.geom,a.geom) order by statefp10"
								cursor.execute(sqlComm)
								states = cursor.fetchall()
								conn.commit()
								starttimeCompany = time.time()
								for s in states:
									sqlComm = "select distinct(countyfp10) as countyfp10 from census.county2010 a, swat.coverageright201301lte b " + \
											"where statefp10='" + s[0] + "' and b.entity='" + company + "' and st_intersects(b.geom,a.geom) order by countyfp10"
									cursor.execute(sqlComm)
									counties = cursor.fetchall()
									conn.commit()
									starttimeState = time.time()
									for c in counties:
										starttimeCounty = time.time()
										print "process " + company + " for state " + s[0] + " county " + c[0] + " start at " + time.strftime("%H:%M:%S", time.localtime(starttimeCounty))
										sqlComm ="insert into " + schema + "." + tableName + " select b.entity,b.protocol,a.geoid10, " + \
												 "CASE " + \
												 "WHEN ST_WITHIN(a.geom, b.geom) THEN 1 " + \
												 "ELSE st_area(st_intersection(st_intersection(st_envelope(a.geom),b.geom),a.geom))/st_area(a.geom) " + \
												 "END " + \
												 "from census.block2010_" + s[0] + " a, swat.coverageright201301lte b " + \
												 "where b.entity='" + company + "' and a.countyfp10='" + c[0] + "' and st_intersects(st_envelope(a.geom),b.geom)"
										cursor.execute(sqlComm)
										conn.commit()
										print "process " + company + " for state " + s[0] + " county " + c[0] + " takes " + str(int((time.time()-starttimeCounty)/60)) + " minutes"
									print "process " + company + " for state " + s[0] + " takes " + str(int((time.time()-starttimeState)/60))+ " minutes"	
								print "process " + company + " takes " + str(int((time.time()-starttimeCompany)/60))+ " minutes"				
		print "Whole Process taken in " + str(int((time.time()-starttime)/60)) + " minutes"
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