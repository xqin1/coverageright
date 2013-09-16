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
		rootDir = "C:\\projects\\Data\\americaroamer\\2013 Jan\\Carriers"
		#conn_string = "host='165.135.239.38' dbname='gisdb' user='bbmap' password='bbmap_ps'"	
		host = "localhost"
		dbname = "gisdb20" 
		schema = "swat"
		tableName = "coverageright201301LTE"
		user = "postgres"
		password = "xiali19690326!A"
		conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"	 

		conn = psycopg2.connect(conn_string)
		cursor = conn.cursor()
		techCount = 0
		companyCount = 0
		sqlComm = "DROP TABLE IF EXISTS " + schema + "." + tableName + " CASCADE"
		cursor.execute(sqlComm)
		conn.commit()
		sqlComm = "CREATE TABLE " + schema + "." + tableName + " (entity varchar(100), protocol varchar(100), geom geometry)"
		cursor.execute(sqlComm)
		conn.commit()

		# cursor.execute(sqlComm)
		# conn.commit()
		for techType in os.listdir(rootDir):
		    techTypeDir = rootDir + "\\" + techType
		    if techType == "LTE":
			    for company in os.listdir(techTypeDir):
			    	print techType + " " + company
			    	shapeFileDir = techTypeDir + "\\" + company + "\\SHP"
			    	for shapeFile in os.listdir(shapeFileDir):
						if shapeFile.endswith("shp"):
							sqlComm = "DROP TABLE IF EXISTS swat." + shapeFile.replace(".shp","") + " CASCADE"
							cursor.execute(sqlComm)
							sqlComm ="CREATE TABLE swat." + shapeFile.replace(".shp","") + "(" + \
					  				 "CONSTRAINT dims_geom CHECK (st_ndims(geom) = 2)," + \
	  				   				 "CONSTRAINT geom CHECK ((geometrytype(geom) = ANY (ARRAY['MULTIPOLYGON'::text, 'POLYGON'::text])) OR geom IS NULL)," + \
	  								 "CONSTRAINT srid_geom CHECK (st_srid(geom) = 4326)) " + \
									 "INHERITS (swat.coverageright201301LTE);"
							cursor.execute(sqlComm)
							conn.commit()

							sqlComm = "drop table if EXISTS " + schema + "." + shapeFile.replace(".shp","") + "_temp" + " CASCADE"
							cursor.execute(sqlComm)
							conn.commit()
							shpComm = 'shp2pgsql -s 4326 -d -I -W latin1 -g geom "' + shapeFileDir + "\\" + shapeFile + '" ' + schema + "." + shapeFile.replace(".shp","") + "_temp | psql -h " + host + " -d " + dbname + " -U " + user
							print "load " + shapeFile + " to postgres"
							shpP = subprocess.call(shpComm,shell=True)
							#To do: repare geometry,do not use ST_MAKEVALID, takes forever, instead use st_buffer
							#update swat.c_spire_wireless_lte set geom = st_buffer(geom,0.0) where st_isvalid(geom) = false
							sqlComm = "insert into " + schema + "." + shapeFile.replace(".shp","") + " select '" + company + "','" + techType + "', geom from " +  schema + "." + shapeFile.replace(".shp","") + "_temp"
							print sqlComm
							cursor.execute(sqlComm)
							conn.commit()

							sqlComm  = "CREATE INDEX " + shapeFile.replace(".shp","") + "_geom_gist ON " + schema + "." + shapeFile.replace(".shp","") + " USING gist (geom )"
							cursor.execute(sqlComm)
							conn.commit()
							#TO DO: use vacuum analyze
							sqlComm = "drop table if EXISTS " + schema + "." + shapeFile.replace(".shp","") + "_temp" + " CASCADE"
							cursor.execute(sqlComm)
							conn.commit()		

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