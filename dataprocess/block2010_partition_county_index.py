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
		#conn_string = "host='165.135.239.38' dbname='gisdb' user='bbmap' password='bbmap_ps'"	
		host = "localhost"
		dbname = "gisdb20" 
		schema = "census"
		tableName = "block2010"
		user = "postgres"
		password = "xiali19690326!A"
		conn_string = "host='" + host + "' dbname='" + dbname + "' user='" + user + "' password='" + password + "'"	 
		conn = psycopg2.connect(conn_string)
		cursor = conn.cursor()
		statefp = ("01","02","04","05","06","08","09","10","11","12","13","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50","51","53","54","55","56","60","66","69","72","78")
		for s in statefp:
			sqlComm  = "CREATE INDEX block2010_" + s +"_county_idx ON census.block2010_"+ s + " USING btree (countyfp10)"
			cursor.execute(sqlComm)
			conn.commit()

			print "create index on " + s
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