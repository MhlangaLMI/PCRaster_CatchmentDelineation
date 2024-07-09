import os
import glob
from pcraster import *
from osgeo import gdal, gdalconst

def mosaic(inputpattern, outputmosaic):
    InputFiles = glob.glob(inputpattern)
    mosaic = gdal.BuildVRT(outputmosaic, InputFiles)
    mosaic.FlushCache()

def reprojectAndClip(inputraster, outputraster, projection, shapefile, resolution):
    if not os.path.exists(shapefile):
        print(f"Warning: Shapefile {shapefile} not found. Skipping clipping step.")
        # Reproject without clipping
        options = gdal.WarpOptions(format='GTIFF',
                                   dstSRS=projection,
                                   xRes=resolution,
                                   yRes=resolution)
        outimage = gdal.Warp(srcDSOrSrcDSTab=inputraster,
                             destNameOrDestDS=outputraster,
                             options=options)
    else:
        options = gdal.WarpOptions(cutlineDSName=shapefile,
                                   cropToCutline=True,
                                   format='GTIFF',
                                   dstSRS=projection,
                                   xRes=resolution,
                                   yRes=resolution)
        outimage = gdal.Warp(srcDSOrSrcDSTab=inputraster,
                             destNameOrDestDS=outputraster,
                             options=options)

def ConvertToPCRaster(src_filename, dst_filename, ot, VS):
    # Open existing dataset
    src_ds = gdal.Open(src_filename)

    # GDAL Translate
    dst_ds = gdal.Translate(dst_filename, src_ds, format='PCRaster', outputType=ot, metadataOptions=VS)

    # Properly close the datasets to flush to disk
    dst_ds = None
    src_ds = None

def CalculateFlowDirection(DEMFile):
    DEM = readmap(DEMFile)
    FlowDirectionMap = lddcreate(DEM, 1e31, 1e31, 1e31, 1e31)
    return FlowDirectionMap

def StreamDelineation(FlowDirectionMap, Threshold):
    StrahlerOrders = streamorder(FlowDirectionMap)
    Stream = ifthen(StrahlerOrders >= Threshold, boolean(1))
    return Stream

# Define inputs and settings
TileExtension = '*.tif'
MosaicOutput = 'mosaic.vrt'
BoundaryPolygon = 'boundingbox.shp'
OutputProjection = 'EPSG:32735' #Must be verified by user
OutputSpatialResolution = 30.0 #Must be verified by user
DEMSubsetOutput = 'DEMsubset.tif'
PCRasterDEMOutput = 'dem.map'
FlowDirectionOutput = 'flowdir.map' 

# Apply stream delineation workflow
print('Creating mosaic...')
mosaic(TileExtension, MosaicOutput)
print('Done!')

print('Reprojecting and clipping...')
reprojectAndClip(MosaicOutput, DEMSubsetOutput, OutputProjection, BoundaryPolygon, OutputSpatialResolution)
print('Done!')

print('Converting to PCRaster format...')
ConvertToPCRaster(DEMSubsetOutput, PCRasterDEMOutput, gdalconst.GDT_Float32, "VS_SCALAR")
print('Done!')

print('Calculating flow direction...')
setclone(PCRasterDEMOutput)
FlowDirection = CalculateFlowDirection(PCRasterDEMOutput)
print('Done!')

for threshold in range(1, 11):
    print(f'Delineating channels with Strahler Order Threshold {threshold}...')
    River = StreamDelineation(FlowDirection, threshold)
    report(River, f'channels_{threshold}.map')
    print(f'Done for Strahler Order Threshold {threshold}')

print('Stream delineation completed and reported.')
