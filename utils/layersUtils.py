from qgis.core import (
    QgsVectorLayer,
    QgsMapLayer
)


def isEmptyVector(layer_path: str, layer_dict: dict) -> bool:
    """ Check whether a vector layer has no features """
    if layer_dict[layer_path] is None:
        layer_dict[layer_path] = QgsVectorLayer(layer_path, '', 'ogr')

    if layer_dict[layer_path].type() == QgsMapLayer.VectorLayer:
        if layer_dict[layer_path].featureCount() == 0:
            return True
    return False
