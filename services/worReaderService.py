from ..config.projections import CRSPREFIX
from qgis.core import (
    QgsProcessingFeedback
)


def readCrsFromWor(worFile: str, feedback: QgsProcessingFeedback) -> list[str]:
    with open(worFile, "r") as f:
        line = f.readline()
        crsString = ""
        feedback.pushInfo(CRSPREFIX)
        while line and not crsString:
            if feedback.isCanceled():
                break
            line = line.strip(" \n")
            # feedback.pushInfo("read line: {}".format(line))
            if line.startswith(CRSPREFIX):
                crsString = line.removeprefix(CRSPREFIX).strip()
            line = f.readline()
    feedback.pushInfo("found coordSys: {}".format(crsString))
    coordsysList = crsString.split(", ")
    return coordsysList
