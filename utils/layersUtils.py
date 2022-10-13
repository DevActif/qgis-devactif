from qgis.core import (QgsRasterLayer,
                       QgsVectorLayer,
                       QgsMapLayer
                       )


def isEmptyVector(layer_path, layer_dict):
    """ Check whether a vector layer has no features """
    if layer_dict[layer_path] is None:
        layer_dict[layer_path] = get_vector_layer(
            layer_path, '', layer_dict)

    if layer_dict[layer_path].type() == QgsMapLayer.VectorLayer:
        if layer_dict[layer_path].featureCount() == 0:
            return True
    return False


def get_vector_layer(layer_path, layer_name, layer_dict, rename=False):
    res = layer_dict[layer_path]
    if res is None:
        res = QgsVectorLayer(layer_path, layer_name, 'ogr')
    elif rename:
        res.setName(layer_name)

    return res


def get_raster_layer(layer_path, layer_name, layer_dict, rename=False):
    res = layer_dict[layer_path]
    if res is None:
        res = QgsRasterLayer(layer_path, layer_name, 'ogr')
    elif rename:
        res.setName(layer_name)

    return res


def createVectorLayer(layer_path, layer_base_name, files_to_load):
    """ Create a vector layer """
    files_to_load[layer_path] = get_vector_layer(
        layer_path, layer_base_name, files_to_load, True)

    return files_to_load[layer_path]


def createRasterLayer(layer_path, layer_base_name, files_to_load):
    """ Create a raster layer """
    files_to_load[layer_path] = get_raster_layer(
        layer_path, layer_base_name, files_to_load, True)

    return files_to_load[layer_path]
