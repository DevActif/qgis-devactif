from qgis.core import (QgsProcessingException, QgsProcessingFeedback)
from ..config.projections import CRSPREFIX, OPENTABLE, COORDSYS_PARAMETERS_COUNT, DATUMS_PARAMETERS_COUNT, PROJECTIONSTRING, datums
import re
import os

def readLayersFromWor(worFile: str) -> list[str]:
    with open(worFile, "r") as f:
        foundOpenTable = False
        line = f.readline()
        arrayLayers = []
        while line:
            line = line.strip(" \n")
            if line.startswith(OPENTABLE):
                path = re.findall('"([^"]*)"', line)[0]
                path = os.path.basename(path)
                path = os.path.normpath(path)
                path = os.path.normcase(path)
                path = os.path.splitext(path)[0]
                layerName = re.findall('As (.*) Interactive', line)[0]
                arrayLayers.append({'path': path, 'layerName': layerName})
                foundOpenTable = True
            elif foundOpenTable:
                break
            line = f.readline()
    return arrayLayers
