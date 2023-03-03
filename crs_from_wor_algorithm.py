# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Crs from wor
                                 A QGIS plugin
 Read coordsys line from wor file and extract epsg crs
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-10-05
        copyright            : (C) 2022 by DevActif
        email                : info@devactif.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'DevActif'
__date__ = '2022-10-05'
__copyright__ = '(C) 2022 by DevActif'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsCoordinateReferenceSystem,
    QgsProcessingException,
    QgsProcessingOutputString,
)
from .services.worService import extractEpsgId, readCrsFromWor


class CrsFromWorAlgorithm(QgsProcessingAlgorithm):
    """
    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'Input'
    OUTPUT = "Crs"
    FOLDER = "Folder"

    crs = QgsCoordinateReferenceSystem()

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('MapInfo Workspace file'),
                extension="wor"
            )
        )

        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT,
                self.tr("Project CRS from .wor")
            )
        )

        self.addOutput(
            QgsProcessingOutputString(
                self.FOLDER,
                self.tr(".wor folder")
            )
        )

    def prepareAlgorithm(self, parameters, context, feedback):
        self.worFile = self.parameterAsFile(parameters, self.INPUT, context)

        coordsysList = readCrsFromWor(self.worFile, feedback)
        epsgId = extractEpsgId(coordsysList)

        if(not epsgId):
            return False

        self.crs.createFromOgcWmsCrs(epsgId)

        if(not self.crs.isValid()):
            raise QgsProcessingException("The crs is not valid")

        return True

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        feedback.setProgressText("Changing CRS and ellipsoid")

        self.originalCRS = context.project().crs()
        self.originalEllipsoid = context.project().ellipsoid()

        context.project().setCrs(self.crs, True)

        feedback.pushInfo("original CRS is {}".format(self.originalCRS))
        feedback.pushInfo("CRS is now {}".format(context.project().crs()))
        feedback.pushInfo(
            "original ellipsoid is {}".format(self.originalEllipsoid))
        feedback.pushInfo("Ellipsoid is now {}".format(
            context.project().ellipsoid()))

        folder = os.path.dirname(self.worFile)


        if feedback.isCanceled():
            self.resetCrs()
            return

        return {self.OUTPUT: self.crs, self.FOLDER: folder}

    def resetCrs(self, context):
        context.project().setCrs(self.originalCRS)
        context.project().setEllipsoid(self.originalEllipsoid)

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'crsfromwor'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Crs from wor")

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CrsFromWorAlgorithm()
