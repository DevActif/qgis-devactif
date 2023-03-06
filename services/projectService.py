from qgis.core import (QgsProcessingFeedback, QgsCoordinateReferenceSystem)
import os

class projectService():

    def __init__(self, project):
        self.project = project

    def changeCRS(self, crs: QgsCoordinateReferenceSystem, feedback: QgsProcessingFeedback):
        feedback.setProgressText("Changing CRS and ellipsoid")

        self.originalCRS = self.project.crs()
        self.originalEllipsoid = self.project.ellipsoid()

        self.project.setCrs(crs, True)

        feedback.pushInfo("original CRS is {}".format(self.originalCRS))
        feedback.pushInfo("CRS is now {}".format(self.project.crs()))
        feedback.pushInfo("original ellipsoid is {}".format(self.originalEllipsoid))
        feedback.pushInfo("Ellipsoid is now {}".format(self.project.ellipsoid()))

    def setFilename(self, worFile: str):
        self.project.setFileName(os.path.basename(worFile))

    def resetCrs(self, feedback: QgsProcessingFeedback):
        self.project.setCrs(self.originalCRS)
        self.project.setEllipsoid(self.originalEllipsoid)
        feedback.pushInfo('CRS and ellipsoid are reinitialized to their original values.')

