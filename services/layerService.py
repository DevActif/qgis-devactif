import os

def extractLayerName(layer_path: str) -> str:
    baseName = os.path.basename(layer_path)
    layerName = os.path.splitext(baseName)[0]

    # Let's clear the layer name for sublayers
    if '|layername=' in baseName and not baseName.endswith('|layername='):
        subLayerName = baseName.split('|layername=')[
            1].split('|geometrytype=')[0]
        layerName = "".join([layerName, " ", subLayerName])
    return layerName

def countFiles(folder:str)->int:
    totalFileCount = 0
    for root, dirs, files in os.walk(folder):
        for file_ in files:
            totalFileCount += 1
    return totalFileCount
