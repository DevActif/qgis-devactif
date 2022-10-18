import os
from ..config.app import RASTER, VECTOR
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProcessingFeedback,
    QgsMapLayer,
    QgsCoordinateReferenceSystem
)


def createLayers(layersToLoad: dict[QgsMapLayer], outputLayers: list[QgsMapLayer], crs: QgsCoordinateReferenceSystem, feedback: QgsProcessingFeedback, dataType: str, numLayers: int, step: int = 0) -> list[QgsMapLayer]:
    for layer_path, layer in layersToLoad.items():
        if feedback.isCanceled():
            return False

        layerName = extractLayerName(layer_path)

        if layer is None:
            if dataType == RASTER:
                layer = QgsRasterLayer(layer_path, layerName)
            elif dataType == VECTOR:
                layer = QgsVectorLayer(layer_path, layerName, 'ogr')
        else:
            layer.setName(layerName)

        if layer and layer.isValid():
            layer.setCrs(crs)
            outputLayers.append(layer)

        step += 1
        feedback.setProcessedCount(step)
        feedback.setProgress(step/numLayers)
    return outputLayers


def extractLayerName(layer_path: str) -> str:
    baseName = os.path.basename(layer_path)
    layerName = os.path.splitext(baseName)[0]

    # Let's clear the layer name for sublayers
    if '|layername=' in baseName and not baseName.endswith('|layername='):
        subLayerName = baseName.split('|layername=')[
            1].split('|geometrytype=')[0]
        layerName = "".join([layerName, " ", subLayerName])
    return layerName
