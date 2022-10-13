from .config.projections import COORDSYS_PARAMETERS_COUNT, DATUMS_PARAMETERS_COUNT, PROJECTIONSTRING, datums


def extractEpsgId(coordsysList, feedback):
    if(len(coordsysList) != COORDSYS_PARAMETERS_COUNT):
        feedback.reportError("The CoordSys string is not 8 parameters",True)
        return False

    if(not coordsysList[0].startswith(PROJECTIONSTRING)):
        feedback.reportError("The projection is not yet implemented",True)
        return False

    mapInfoDatumId = int(coordsysList[1])
    if(mapInfoDatumId not in datums):
        feedback.reportError("The datum is not yet implemented",True)
        return False

    if(len(datums[mapInfoDatumId]) != DATUMS_PARAMETERS_COUNT):
        feedback.reportError("The datum is not completely configured",True)
        return False

    epsgId = datums[mapInfoDatumId][3]
    
    return epsgId