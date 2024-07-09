import os
from pcraster import *

def col2map(x, y, clone):
    with open('location.txt', 'w') as f:
        f.write(str(x) + ' ' + str(y) + ' 1')
    cmd = 'col2map -N location.txt location.map --clone {0}'.format(clone)
    os.system(cmd)
    Map = readmap('location.map')
    return Map

def CalculateFlowDirection(DEMFile):
    DEM = readmap(DEMFile)
    FlowDirectionMap = lddcreate(DEM, 1e31, 1e31, 1e31, 1e31)
    return FlowDirectionMap

# Define inputs and settings
FlowDirectionOutput = 'flowdir.map'
PCRasterDEMOutput = 'dem.map'
FlowDirection = CalculateFlowDirection(PCRasterDEMOutput)
OutletX = 433222.60
OutletY = 6318929.49

print('Delineating the catchment for Strahler Order Threshold 1...')
Outlet = col2map(OutletX, OutletY, PCRasterDEMOutput)
CatchmentArea = catchment(FlowDirection, Outlet)
report(CatchmentArea, 'catchment_1.map')
print('Done for Strahler Order Threshold 1')

print('Catchment delineation completed and reported.')
