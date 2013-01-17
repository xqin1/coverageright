# Spatial Data Processing and Visualization

### Problem to Solve:

+ We have ~400 shape files depicting carrier footprint by protocol quarterly.
+ Analyst need to view, compare these footprints by carrier and protocol. Currently they rely on GIS             tech to create the map
+ A simple web-based viewer is needed to satisfy this requirement

****

### Technology stack:

+ [ogr2ogr](http://www.gdal.org/ogr2ogr.html): extract metadata from Shape file
+ [ArcPy](http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//000v00000001000000): dissolve boundaries to one multiPolygon for each Shape file
+ [curl](http://curl.haxx.se/): publish Shape file to [GeoServer](http://geoserver.org) using [GeoServer REST API](http://docs.geoserver.org/stable/en/user/restconfig/rest-config-api.html)
+ [Psycopg 2](http://initd.org/psycopg/docs/): Python module for [PostgreSQL](http://www.postgresql.org/) adapter
+ *shp2pgsql* tool shipped with [PostGIS](http://postgis.refractions.net/)
+ [OpenLayers](http://openlayers.org): client mapping library
****

### Approach 1: Publish Shape File Directly

### Steps

+ Run **geoserver_pub.py**
    + loop through each shape file in the directory
    + use *ogg2ogr* to extract extent information
    + use *curl* to publish the shape file to GeoServer as map service
    + generate a *JSON* file to be used on client side mapping

            [
                {
                    "property": [
                                    {
                                        "companyName": "ACS Wireless", 
                                        "extent": [
                                                -165.97391, 
                                                54.731114, 
                                                -130.378126, 
                                                71.40634], 
                                        "id": 1, 
                                        "serviceName": "ACS_Wireless_1X"
                                    },
                                .....
                                ]
                   "serviceType": "EDGE"
                },
                  ......   
            ]     
+ consume GeoServer WMS service on client side **(app_shape.js)**

#### PROS
+ straightforward and can be done within an hour
+ no proprietary software required

#### CONS
+ individual Shape file needs to be published as map service and make it hard to manage
+ not flexible to manage data from multiple submissions
+ some shape files are quite large and it may cause performance issues

### Approach 2: load shape file to Postgres

### Steps

+ Run **arcpy_dissolve.py**
    + loop through each shape file in the directory
    + use *arcpy.Dissolve_management* to dissolve boundaries to one multiPolygon
+ Run **loadShp.py**
    + loop through each dissolved shape file in the directory
    + use *shp2pgsql* to load the shape file to Postgres table
    + use *psycopg2* command to insert the dissolved record into final table
    + generate a *JSON* file as in Approach 1 to be used on client side mapping
    + publish final table to GeoServer  
+ consume GeoServer WMS service on client side **(app.js)**

#### PROS
+ there is only one table to deal with and data from other submissions can be easily added
+ *dissolved* boundary is generally smaller than original data and can be easily simplified to further reduce the size if necessary, thus boosting the performance

#### CONS
+ for some shape files with large size, complex geometries or non-OGC-compliant geometries, *st_union* would fail miserably, thus ArcGIS comes into play
+ in some instances, the final dissolved shape file is not valid resulting from ArcPy script. But running throung ArcGIS Desktop will produce the correct result. 
+ time consuming and sometimes need human intervention, thus it's semi-auto process