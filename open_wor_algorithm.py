# -*- coding: utf-8 -*-

"""
/***************************************************************************
 OpenWor
                                 A QGIS plugin
 Open a wor file using crsfromwor and Layers Loader processing algorithms
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
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFile,
    QgsProcessingAlgorithm)
from .services.worService import readLayersFromWor
from .services.projectService import projectService
from .services.layerService import loadLayersOnCompletion, getFilesList, chooseFileFromLayerPath, createLayer

class OpenWorAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'Input'
    CRS = 'CRS'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('MapInfo Workspace file'),
                extension="wor"
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Coordinate Reference System')
            )
        )

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        prjService = projectService(context.project())

        feedback.setCurrentStep(0)
        worFile = self.parameterAsFile(parameters, self.INPUT, context)
        crs = self.parameterAsCrs(parameters, self.CRS, context)

        folder = os.path.dirname(worFile)
        feedback.setProgressText("Reading layers from wor file")
        layers = readLayersFromWor(worFile)

        prjService.setFilename(worFile)
        prjService.changeCRS(crs, feedback)
        
        if feedback.isCanceled():
            prjService.resetCrs(feedback)
            return

        outputLayers = {}
        currentLayer = 0
        feedback.setProgressText('Listing files in folder')
        listFiles = getFilesList(folder)
        layersCount = len(layers)
        feedback.pushInfo("there is {} files in the folder {}".format(len(listFiles), folder))

        feedback.setProgressText("Associating layers with files")
        feedback.setCurrentStep(1)
        for layer in layers:
            if feedback.isCanceled():
                prjService.resetCrs()
                return False
            feedback.setProgress(currentLayer/layersCount * 100)
            currentLayer += 1

            try:
                suitor = chooseFileFromLayerPath(layer['path'], listFiles)
            except ValueError as err:
                feedback.reportError('Layer '+ err.args[1] + ' not found in the folder.')
                continue

            qgsLayer = createLayer(suitor, folder, layer, crs)

            if(qgsLayer):
                outputLayers[layer['layerName']] = qgsLayer

        feedback.pushInfo("there is {} valid layers".format(len(outputLayers)))
        loadLayersOnCompletion(outputLayers, context)
            
        return outputLayers

    def name(self):
        return 'openwor'

    def displayName(self):
        return self.tr("Open wor")

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return OpenWorAlgorithm()
