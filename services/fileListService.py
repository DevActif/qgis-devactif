import os
from ..config.app import RASTER, VECTOR
from qgis.core import (
    QgsVectorLayer,
    QgsProcessingFeedback

)
from ..utils.layersUtils import isEmptyVector


def getFilesToLoad(folder: str, dataType: str, feedback: QgsProcessingFeedback) -> dict:
    """ Go through directories to fill a list with layers ready to be loaded """
    layer_dict = dict()  # {'layer_path_1': layer_obj_1, ...}

    for root, dirs, files in os.walk(folder):
        for file_ in files:
            if feedback.isCanceled():
                return False

            layer_path = os.path.join(root, file_)

            if dataType == VECTOR:
                layer = QgsVectorLayer(layer_path, "", "ogr")
                if not layer.isValid():
                    next
                # Do we have sublayers?
                if len(layer.dataProvider().subLayers()) > 1:
                    layer_dict = loadSubLayers(layer_dict, layer, layer_path)
                else:
                    layer_dict[layer_path] = layer
            elif dataType == RASTER:
                layer_dict[layer_path] = None

    files_to_load = dict()
    for path in layer_dict:
        if feedback.isCanceled():
            return False

        if dataType == "raster" or not isEmptyVector(path, layer_dict):
            files_to_load[path] = layer_dict.get(path, None)

    return files_to_load


def loadSubLayers(layer_dict: dict, layer: QgsVectorLayer, layer_path: str) -> dict:
    # Sample: ['0!!::!!line_intersection_collection!!::!!12!!::!!LineString!!::!!geometryProperty']
    subLayers = dict()
    for subLayer in layer.dataProvider().subLayers():
        # 1: name, 3: geometry type
        parts = subLayer.split("!!::!!")
        # Sublayers might share layer name, we need to get geometry types just in case
        if parts[1] in subLayers:
            subLayers[parts[1]].append(parts[3])
        else:
            subLayers[parts[1]] = [parts[3]]

    for subLayerName, subLayerGeometries in subLayers.items():
        if len(subLayerGeometries) > 1:
            for subLayerGeometry in subLayerGeometries:
                layer_dict["{}|layername={}|geometrytype={}".format(layer_path,
                                                                    subLayerName,
                                                                    subLayerGeometry)] = None
        else:
            layer_dict["{}|layername={}".format(
                layer_path, subLayerName)] = None

    return layer_dict
