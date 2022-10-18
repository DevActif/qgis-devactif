from qgis.core import (QgsProcessingException,)
from ..config.projections import COORDSYS_PARAMETERS_COUNT, DATUMS_PARAMETERS_COUNT, PROJECTIONSTRING, datums


def extractEpsgId(coordsysList, feedback):
    if(len(coordsysList) != COORDSYS_PARAMETERS_COUNT):
        raise QgsProcessingException("The CoordSys string is not 8 parameters")

    if(not coordsysList[0].startswith(PROJECTIONSTRING)):
        raise QgsProcessingException("The projection is not yet implemented")

    mapInfoDatumId = int(coordsysList[1])
    if(mapInfoDatumId not in datums):
        raise QgsProcessingException("The datum is not yet implemented")

    if(len(datums[mapInfoDatumId]) != DATUMS_PARAMETERS_COUNT):
        raise QgsProcessingException("The datum is not completely configured")

    epsgId = datums[mapInfoDatumId][3]

    return epsgId
