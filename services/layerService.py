from qgis.core import (QgsProcessingContext, QgsRasterLayer, QgsVectorLayer)
import os
from ..config.extensions import RASTER, VECTOR


def createLayer(suitor, folder, layer, crs, feedback):
    path = os.path.join(folder, suitor['file'])

    if suitor['type'] == RASTER:
        qgsLayer = QgsRasterLayer(path, layer['layerName'])
    elif suitor['type'] == VECTOR:
        qgsLayer = QgsVectorLayer(path, layer['layerName'], 'ogr')
    else:
        feedback.reportError(
            "Layer {} has problems which are not supposed to occurs".format(layer["layerName"]))
        return

    if qgsLayer.isValid():
        qgsLayer.setCrs(crs)
        return qgsLayer
    else:
        feedback.reportError(
            "Layer {} was associated with {} but produce an invalid layer. Try changing extensions priority.".format(layer["layerName"], path))


def getFilesList(folder: str) -> list[str]:
    listFiles = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            path = os.path.normpath(path)
            path = os.path.normcase(path)
            listFiles.append(os.path.relpath(path, folder))
    return listFiles


def chooseFileFromLayerPath(path: str, files: list[str], raster_priorities: str, vector_priorities: str) -> object:
    listSuitors = []
    rasters = raster_priorities.split(',')
    vectors = vector_priorities.split(',')
    allExtensions = rasters + vectors
    for file in files:
        if file.__contains__(path):
            extension = os.path.splitext(file)[1]
            if extension in allExtensions:
                layerType = RASTER if extension in rasters else VECTOR
                listSuitors.append({'file': file, 'extension': extension, 'priority': allExtensions.index(
                    extension), 'type': layerType})

    listSuitors = sorted(listSuitors, key=getSuitorKeySort)

    if len(listSuitors) > 0:
        return listSuitors[0]
    else:
        raise ValueError('Suitor not found.', path)

def loadLayersOnCompletion(outputLayers: list[object], context: QgsProcessingContext):
    for name, qgsLayer in outputLayers.items():
        context.temporaryLayerStore().addMapLayer(qgsLayer)
        context.addLayerToLoadOnCompletion(
            qgsLayer.id(), QgsProcessingContext.LayerDetails(name=name, project=context.project()))


def getSuitorKeySort(suitor: object) -> int:
    return suitor['priority']


def countFiles(folder: str) -> int:
    totalFileCount = 0
    for root, dirs, files in os.walk(folder):
        for file_ in files:
            totalFileCount += 1
    return totalFileCount
