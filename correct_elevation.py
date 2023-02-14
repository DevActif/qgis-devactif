# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsGeometry,
                       QgsFeature,
                       QgsMultiLineString
                       )
from qgis import processing


class ProcessingParameters:
    def __init__(self, grade: float, origin_x: float, origin_y: float):
        self.grade = grade
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.maxDistance = 0


class CorrectElevationFromGrade(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    GRADE = 'GRADE'
    ORIGIN_X = 'ORIGIN_x'
    ORIGIN_Y = 'ORIGIN_Y'

    # def flags(self):
    #     return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CorrectElevationFromGrade()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'correctelevation'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return "Correct elevation from grade"

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Correct z elevation with a grade starting from origin point")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Corrected elevation')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.GRADE,
                self.tr('Grade %'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.4
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ORIGIN_X,
                self.tr('Origin point X'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=500000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ORIGIN_Y,
                self.tr('Origin point Y'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=5000000
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        grade = self.parameterAsDouble(
            parameters,
            self.GRADE,
            context
        )

        origin_x = self.parameterAsDouble(
            parameters,
            self.ORIGIN_X,
            context
        )

        origin_y = self.parameterAsDouble(
            parameters,
            self.ORIGIN_Y,
            context
        )
        processingParameters = ProcessingParameters(grade, origin_x, origin_y)

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT))

        feedback.pushInfo(
            'number of features: {}'.format(source.featureCount()))
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            geometry = feature.geometry()

            self.geometryIterator(
                geometry.get(), processingParameters, 1, feedback)

            newFeature = QgsFeature()
            newFeature.setAttributes(feature.attributes())
            newFeature.setGeometry(QgsGeometry(geometry))
            # Add a feature in the sink
            sink.addFeature(newFeature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        feedback.pushInfo('max distance: {}'.format(
            processingParameters.maxDistance))

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}

    def adjustPoint(self, geo: QgsMultiLineString, parameters: ProcessingParameters, feedback):
        for indexPoint in range(geo.childCount()):
            point = geo.pointN(indexPoint)
            distance = point.distance(parameters.origin_x, parameters.origin_y)
            parameters.maxDistance = max(distance, parameters.maxDistance)
            newZ = point.z() + distance * parameters.grade/100.0

            # feedback.pushInfo('distance: ' + str(distance))
            # feedback.pushInfo('initial z: ' + str(point.z()))
            # feedback.pushInfo('modified z: ' + str(newZ))
            geo.setZAt(indexPoint, round(newZ, 3))

    def geometryIterator(self, geo: QgsGeometry, parameters: ProcessingParameters, iterationDepth: int, feedback) -> bool:
        if(iterationDepth > 5):
            return
        for indexChild in range(geo.childCount()):
            childGeo = geo.childGeometry(indexChild)
            if(childGeo.geometryType() == "LineString"):
                self.adjustPoint(childGeo, parameters, feedback)
            else:
                self.geometryIterator(
                    childGeo, parameters, iterationDepth+1, feedback)
