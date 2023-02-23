from qgis.core import (QgsProcessingException, QgsProcessingFeedback)
from ..config.projections import CRSPREFIX, OPENTABLE, COORDSYS_PARAMETERS_COUNT, DATUMS_PARAMETERS_COUNT, PROJECTIONSTRING, datums


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


def readCrsFromWor(worFile: str, feedback: QgsProcessingFeedback) -> list[str]:
    with open(worFile, "r") as f:
        line = f.readline()
        crsString = ""
        arrayLayers = []
        totalLayerCount = 0
        feedback.pushInfo(CRSPREFIX)
        while line and not crsString:
            if feedback.isCanceled():
                break
            line = line.strip(" \n")
            # feedback.pushInfo("read line: {}".format(line))
            if line.startswith(CRSPREFIX):
                crsString = line.removeprefix(CRSPREFIX).strip()
            if line.startswith(OPENTABLE):
                arrayLayers.append(line.removeprefix(OPENTABLE).strip())
            line = f.readline()
    feedback.pushInfo("found coordSys: {}".format(crsString))
    coordsysList = crsString.split(", ")
    for layer in arrayLayers:
        totalLayerCount += 1
    feedback.pushInfo("Numbers of layers found: {}".format(totalLayerCount))
    return coordsysList
