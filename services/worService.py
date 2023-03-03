from qgis.core import (QgsProcessingException, QgsProcessingFeedback)
from ..config.projections import CRSPREFIX, OPENTABLE, COORDSYS_PARAMETERS_COUNT, DATUMS_PARAMETERS_COUNT, PROJECTIONSTRING, datums
import re
import os

def extractEpsgId(coordsys: list) -> str:
    if(len(coordsys) != COORDSYS_PARAMETERS_COUNT):
        raise QgsProcessingException("The CoordSys string is not 8 parameters")

    if(not coordsys[0].startswith(PROJECTIONSTRING)):
        raise QgsProcessingException("The projection is not yet implemented")

    mapInfoDatumId = int(coordsys[1])
    if(mapInfoDatumId not in datums):
        raise QgsProcessingException("The datum is not yet implemented")

    if(len(datums[mapInfoDatumId]) != DATUMS_PARAMETERS_COUNT):
        raise QgsProcessingException("The datum is not completely configured")

    epsgId = datums[mapInfoDatumId][3]

    return epsgId

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

def readCrsFromWor(worFile: str, feedback: QgsProcessingFeedback) -> list[str]:
    with open(worFile, "r") as f:
        line = f.readline()
        crsString = ""
        feedback.pushInfo(CRSPREFIX)
        while line and not crsString:
            if feedback.isCanceled():
                break
            line = line.strip(" \n")
            if line.startswith(CRSPREFIX):
                crsString = line.removeprefix(CRSPREFIX).strip()
            line = f.readline()
    feedback.pushInfo("found coordSys: {}".format(crsString))
    coordsysList = crsString.split(", ")
    return coordsysList


