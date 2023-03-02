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
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsRasterLayer,
    QgsVectorLayer)
from .services.worService import readLayersFromWor
from .services.layerService import getFilesList, chooseFileFromLayerPath
from .config.extensions import RASTER, VECTOR

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
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)

        worFile = self.parameterAsFile(parameters, self.INPUT, context)
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        folder = os.path.dirname(worFile)

        feedback.setProgressText("Searching layers")
        layers = readLayersFromWor(worFile)
        context.project().setFileName(os.path.basename(worFile))

        feedback.setProgressText("Changing CRS and ellipsoid")

        self.originalCRS = context.project().crs()
        self.originalEllipsoid = context.project().ellipsoid()

        context.project().setCrs(crs, True)

        feedback.pushInfo("original CRS is {}".format(self.originalCRS))
        feedback.pushInfo("CRS is now {}".format(context.project().crs()))
        feedback.pushInfo(
            "original ellipsoid is {}".format(self.originalEllipsoid))
        feedback.pushInfo("Ellipsoid is now {}".format(
            context.project().ellipsoid()))

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            self.resetCrs()
            return
        
        listFiles = getFilesList(folder)
        layersCount = len(layers)
        feedback.pushInfo(
            "there is {} files in the folder {}".format(len(listFiles), folder))
        
        outputLayers = {}
        currentLayer = 0
        
        for layer in layers:
            if feedback.isCanceled():
                return False
            feedback.setProgress(currentLayer/layersCount * 100)
            currentLayer += 1

            suitor = chooseFileFromLayerPath(layer['path'], listFiles)

            path = os.path.join(folder, suitor['file'])

            if suitor['type'] == RASTER:
                qgsLayer = QgsRasterLayer(path, layer['layerName'])
            elif suitor['type'] == VECTOR:
                qgsLayer = QgsVectorLayer(path, layer['layerName'], 'ogr')
            else:
                continue
            
            qgsLayer.setCrs(crs)
            outputLayers[layer['layerName']] = qgsLayer

        feedback.pushInfo("there is {} valid layers".format(len(outputLayers)))
        for name, qgsLayer in outputLayers.items():
            context.temporaryLayerStore().addMapLayer(qgsLayer)
            context.addLayerToLoadOnCompletion(
                qgsLayer.id(), QgsProcessingContext.LayerDetails(name=name, project=context.project()))
            
        return outputLayers
    
    def resetCrs(self, context):
        context.project().setCrs(self.originalCRS)
        context.project().setEllipsoid(self.originalEllipsoid)

    def name(self):
        return 'openwor'

    def displayName(self):
        return self.tr("Open wor")

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return OpenWorAlgorithm()
