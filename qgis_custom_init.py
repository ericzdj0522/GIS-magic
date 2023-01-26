import os, sys
sys.path.append('/Applications/QGIS3.10.app/Contents/Resources/python/')
sys.path.append('/Applications/QGIS3.10.app/Contents/Resources/python/plugins')

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/Applications/QGIS3.10.app/Contents/PlugIns'
os.environ['GDAL_DATA'] = '/Applications/QGIS3.10.app/Contents/Resources/gdal/'

from qgis.core import *


def run():
    # Supply path to qgis install location
    QgsApplication.setPrefixPath("/Applications/QGIS3.10.app/Contents/MacOS", True)

    # Create a reference to the QgsApplication.  Setting the
    # second argument to False disables the GUI.
    qgs = QgsApplication([], False)
    print("I finally succeeded!")
    # Load providers
    qgs.initQgis()

    #sys.path.append('/docs/dev/qgis/build/output/python/plugins')

    #import processing module
    #To use native algorithms in a standalone application, you need to add the provider usin
    from qgis.analysis import QgsNativeAlgorithms
    from qgis import processing
    from processing.core.Processing import Processing
    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

    # Write your code here to load some layers, use processing
    # algorithms, etc.
    #Step1: Select online station based on netcloud
    infeature = '/Users/dj/Documents/QGIS/Shapefile/Test/CONUS_Site_20201110.shp'
    incsv = '/Users/dj/Documents/QGIS/CSV/China/CONUS_status.csv'
    shp = QgsVectorLayer(infeature, 'shapelayer')
    #QgsProject.instance().addMapLayer(shp)
    csv = QgsVectorLayer(incsv, 'csvlayer')
    #QgsProject.instance().addMapLayer(csv)

    shpField = 'Swift Site'
    csvField = 'custom1'
    joinObject = QgsVectorLayerJoinInfo()
    joinObject.setJoinFieldName(csvField)
    joinObject.setTargetFieldName(shpField)
    joinObject.setJoinLayerId(csv.id())
    joinObject.setUsingMemoryCache(True)
    joinObject.setJoinLayer(csv)
    shp.addJoin(joinObject)
    shp.selectByExpression("\"csvlayer_state\"= 'online'")
    outfeature = '/Users/dj/Documents/QGIS/Shapefile/Test/CONUS_station_online.shp'
    writer = QgsVectorFileWriter.writeAsVectorFormat(shp, outfeature, 'UTF-8', shp.crs(), driverName="ESRI Shapefile", onlySelected=True)
    #shp_selected = QgsVectorLayer(outfeature, 'selected_layer')
    #QgsProject.instance().addMapLayer(shp_selected)

    #Definitaion for COUNUS customized projection
    crs_wkt = 'PROJCS["unnamed",GEOGCS["GRS 1980(IUGG, 1980)",DATUM["unknown",SPHEROID["GRS80",6378137,298.257222101],TOWGS84[0,0,0,0,0,0,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Equidistant_Conic"],PARAMETER["standard_parallel_1",33],PARAMETER["standard_parallel_2",45],PARAMETER["latitude_of_center",39],PARAMETER["longitude_of_center",-96],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'
    Conus_crs = QgsCoordinateReferenceSystem(crs_wkt)

    # Create Delaunay Triangle
    result = processing.run("qgis:delaunaytriangulation",
                          {'INPUT': outfeature,
                           'OUTPUT': 'memory:triangle'
                           })

    result = processing.run("qgis:polygonstolines",
                          {'INPUT': result['OUTPUT'],
                           'OUTPUT': 'memory:polylines'
                           })

    result = processing.run("qgis:explodelines",
                          {'INPUT': result['OUTPUT'],
                           'OUTPUT': 'memory:explodepolylines'
                           })

    result = processing.run("qgis:deleteduplicategeometries",
                          {'INPUT': result['OUTPUT'],
                           'OUTPUT': 'memory:cleanpolylines'
                           })


    result = processing.run("qgis:reprojectlayer",
                          {'INPUT': result['OUTPUT'],
                           'TARGET_CRS': 'epsg:3857',
                           'OUTPUT': 'memory:Reprojectedpolyline'
                           })

    # Network output, not temporary layer
    Network = '/Users/dj/Documents/QGIS/Shapefile/Test/CONUS_Site_Network_espg3857.shp'
    processing.run("qgis:exportaddgeometrycolumns",
                         {'INPUT': result['OUTPUT'],
                          'CALC_METHOD': 0,
                          'OUTPUT': Network
                          })

    # Finally, exitQgis() is called to remove the
    # provider and layer registries from memory
    qgs.exitQgis()
run()