import os
import re
from ..config.extensions import rasters, vectors, RASTER, VECTOR

def getFilesList(folder: str) -> list[str]:
    listFiles = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            path = os.path.normpath(path)
            path = os.path.normcase(path)
            listFiles.append(os.path.relpath(path, folder))
    return listFiles

def chooseFileFromLayerPath(path: str, files: list[str]) -> object:
    listSuitors = []
    allExtensions = rasters + vectors
    for file in files:
        if file.__contains__(path):
            extension = re.findall('(\..*)$', file)[0]
            if extension in allExtensions:
                layerType = RASTER if extension in rasters else VECTOR
                listSuitors.append({'file': file, 'extension': extension, 'priority': allExtensions.index(extension), 'type': layerType})
    
    listSuitors = sorted(listSuitors, key=getSuitorKeySort)
    
    return listSuitors[0]

def getSuitorKeySort(suitor:object)->int:
    return suitor['priority']

def countFiles(folder:str)->int:
    totalFileCount = 0
    for root, dirs, files in os.walk(folder):
        for file_ in files:
            totalFileCount += 1
    return totalFileCount
