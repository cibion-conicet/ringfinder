# -*- coding: utf-8 -*-
"""
Created on Wed Oct  1 13:41:48 2014

@authors: Luciano Masullo, Federico Barabas
"""

import os
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import ringfinder.utils as utils
from ringfinder.neurosimulations import simAxon
import ringfinder.tools as tools
import ringfinder.pyqtsubclass as pyqtsub


class GollumDeveloper(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.testData = False

        self.setWindowTitle('Gollum Developer')

        self.cwidget = QtGui.QWidget()
        self.setCentralWidget(self.cwidget)

        self.subImgSize = 1000      # subimage size in nm

        # Separate frame for loading controls
        loadTitle = QtGui.QLabel('<b><u>Load Image</u></b>')
        loadTitle.setTextFormat(QtCore.Qt.RichText)
        loadTitle.setAlignment(QtCore.Qt.AlignCenter)
        loadTitle.setStyleSheet("font-size:14px")

        self.STORMPxEdit = QtGui.QLineEdit()
        self.magnificationEdit = QtGui.QLineEdit()
        self.loadSTORMButton = QtGui.QPushButton('Load')
        self.loadSTORMButton.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                           QtGui.QSizePolicy.Expanding)
        self.STEDPxEdit = QtGui.QLineEdit()
        self.loadSTEDButton = QtGui.QPushButton('Load')

        # Ring finding method settings
        preTitle = QtGui.QLabel('<b><u>Pre-analysis</u></b>')
        preTitle.setTextFormat(QtCore.Qt.RichText)
        preTitle.setAlignment(QtCore.Qt.AlignCenter)
        preTitle.setStyleSheet("font-size:14px")
        self.roiSizeEdit = QtGui.QLineEdit()
        sigmaLabel = QtGui.QLabel('Sigma Gaussian filter σ<sub>GF</sub> [nm]')
        self.sigmaEdit = QtGui.QLineEdit()
        iThrTxt = 'Discrimination threshold <i>I<sub>Th</sub></i> [σ]'
        iThrLabel = QtGui.QLabel(iThrTxt)
        self.intThresEdit = QtGui.QLineEdit()
        self.minAreaLabel = QtGui.QLabel('Minimum filled area [%]')
        self.minAreaEdit = QtGui.QLineEdit()
        self.intThrButton = QtGui.QPushButton('Detect neuronal material')
        self.intThrButton.setCheckable(True)
        self.intThrButton.setFixedHeight(28)
        self.filterImageButton = QtGui.QPushButton('Filter Image')
        self.filterImageButton.setFixedHeight(28)
        self.lineLengthLabel = QtGui.QLabel('Direction lines min length [nm]')
        self.lineLengthEdit = QtGui.QLineEdit()
        dirButton = QtGui.QPushButton('Get axon/dendrite orientation')
        dirButton.setFixedHeight(28)

        mpsTitle = QtGui.QLabel('<b><u>MPS quantification</u></b>')
        mpsTitle.setTextFormat(QtCore.Qt.RichText)
        mpsTitle.setAlignment(QtCore.Qt.AlignCenter)
        mpsTitle.setStyleSheet("font-size:14px")

        self.wvlenEdit = QtGui.QLineEdit()
        self.sinPowerLabel = QtGui.QLabel('Sinusoidal pattern power')
        self.sinPowerEdit = QtGui.QLineEdit()
        self.thetaStepLabel = QtGui.QLabel('Angular step [°]')
        self.thetaStepEdit = QtGui.QLineEdit()
        self.deltaThLabel = QtGui.QLabel('Delta Angle [°]')
        self.deltaThEdit = QtGui.QLineEdit()
        corrThresLabel = QtGui.QLabel('Discrimination threshold')
        self.corrThresEdit = QtGui.QLineEdit()

        advButton = QtGui.QPushButton('Advanced options')
        advButton.setCheckable(True)
        advButton.setFixedHeight(28)
        self.advanced = True
        self.toggleAdvanced()
        advButton.clicked.connect(self.toggleAdvanced)

        corrButton = QtGui.QPushButton('Run analysis')
        corrButton.setFixedHeight(28)
        self.resultLabel = QtGui.QLabel()
        self.resultLabel.setAlignment(QtCore.Qt.AlignCenter |
                                      QtCore.Qt.AlignVCenter)
        self.resultLabel.setTextFormat(QtCore.Qt.RichText)

        # Load settings configuration and then connect the update
        try:
            tools.loadConfig(self)
        except:
            tools.saveDefaultConfig()
            tools.loadConfig(self)
        self.STORMPxEdit.editingFinished.connect(self.updateConfig)
        self.magnificationEdit.editingFinished.connect(self.updateConfig)
        self.STEDPxEdit.editingFinished.connect(self.updateConfig)
        self.roiSizeEdit.editingFinished.connect(self.updateConfig)
        self.sigmaEdit.editingFinished.connect(self.updateConfig)
        self.intThresEdit.editingFinished.connect(self.updateConfig)
        self.lineLengthEdit.editingFinished.connect(self.updateConfig)
        self.wvlenEdit.editingFinished.connect(self.updateConfig)
        self.sinPowerEdit.editingFinished.connect(self.updateConfig)
        self.thetaStepEdit.editingFinished.connect(self.updateConfig)
        self.deltaThEdit.editingFinished.connect(self.updateConfig)
        self.corrThresEdit.editingFinished.connect(self.updateConfig)

        buttonWidget = QtGui.QWidget()
        buttonsLayout = QtGui.QGridLayout()
        buttonWidget.setLayout(buttonsLayout)

        buttonsLayout.addWidget(loadTitle, 0, 0, 1, 3)
        buttonsLayout.addWidget(
            QtGui.QLabel('<b>STORM</b> pixel size [nm]'), 1, 0)
        buttonsLayout.addWidget(self.STORMPxEdit, 1, 1)
        buttonsLayout.addWidget(
            QtGui.QLabel('<b>STORM</b> magnification'), 2, 0)
        buttonsLayout.addWidget(self.magnificationEdit, 2, 1)
        buttonsLayout.addWidget(self.loadSTORMButton, 1, 2, 2, 1)
        buttonsLayout.addWidget(
            QtGui.QLabel('<b>STED</b> pixel size [nm]'), 3, 0)
        buttonsLayout.addWidget(self.STEDPxEdit, 3, 1)
        buttonsLayout.addWidget(self.loadSTEDButton, 3, 2)

        buttonsLayout.addWidget(preTitle, 5, 0, 1, 3)
        buttonsLayout.addWidget(sigmaLabel, 6, 0, 1, 2)
        buttonsLayout.addWidget(self.sigmaEdit, 6, 1, 1, 2)
        buttonsLayout.addWidget(iThrLabel, 7, 0, 1, 2)
        buttonsLayout.addWidget(self.intThresEdit, 7, 1, 1, 2)
        buttonsLayout.addWidget(self.minAreaLabel, 8, 0, 1, 2)
        buttonsLayout.addWidget(self.minAreaEdit, 8, 2)
        buttonsLayout.addWidget(self.intThrButton, 9, 0, 1, 3)
        buttonsLayout.addWidget(self.filterImageButton, 10, 0, 1, 3)
        buttonsLayout.addWidget(dirButton, 11, 0, 1, 3)
        buttonsLayout.addWidget(self.lineLengthLabel, 12, 0, 1, 2)
        buttonsLayout.addWidget(self.lineLengthEdit, 12, 2)

        buttonsLayout.addWidget(mpsTitle, 13, 0, 1, 3)
        buttonsLayout.addWidget(QtGui.QLabel('ROI size [nm]'), 14, 0, 1, 2)
        buttonsLayout.addWidget(self.roiSizeEdit, 14, 2)

        buttonsLayout.addWidget(
            QtGui.QLabel('Ring periodicity [nm]'), 15, 0, 1, 2)
        buttonsLayout.addWidget(self.wvlenEdit, 15, 2)
        buttonsLayout.addWidget(self.sinPowerLabel, 16, 0, 1, 2)
        buttonsLayout.addWidget(self.sinPowerEdit, 16, 2)
        buttonsLayout.addWidget(self.thetaStepLabel, 17, 0, 1, 2)
        buttonsLayout.addWidget(self.thetaStepEdit, 17, 2)
        buttonsLayout.addWidget(self.deltaThLabel, 18, 0, 1, 2)
        buttonsLayout.addWidget(self.deltaThEdit, 18, 2)
        buttonsLayout.addWidget(corrThresLabel, 19, 0, 1, 2)
        buttonsLayout.addWidget(self.corrThresEdit, 19, 2)
        buttonsLayout.addWidget(advButton, 20, 0, 1, 3)
        buttonsLayout.addWidget(corrButton, 21, 0, 1, 3)
        buttonsLayout.addWidget(self.resultLabel, 22, 0, 2, 3)
        buttonsLayout.setColumnMinimumWidth(0, 160)
        buttonWidget.setFixedWidth(300)

        # Widgets' layout
        layout = QtGui.QGridLayout()
        self.cwidget.setLayout(layout)
        layout.addWidget(buttonWidget, 0, 0)
        self.imageWidget = ImageWidget(self)
        layout.addWidget(self.imageWidget, 0, 1)
        layout.setColumnMinimumWidth(1, 1060)
        layout.setRowMinimumHeight(0, 820)

        self.roiSizeEdit.textChanged.connect(self.imageWidget.updateROI)
        self.sigmaEdit.textChanged.connect(self.imageWidget.updateMasks)
        self.intThresEdit.textChanged.connect(self.imageWidget.updateMasks)
        self.loadSTORMButton.clicked.connect(self.imageWidget.loadSTORM)
        self.loadSTEDButton.clicked.connect(self.imageWidget.loadSTED)

        self.filterImageButton.clicked.connect(self.imageWidget.imageFilter)
        dirButton.clicked.connect(self.imageWidget.getDirection)
        self.intThrButton.clicked.connect(self.imageWidget.intThreshold)
        corrButton.clicked.connect(self.imageWidget.corrMethodGUI)

    def toggleAdvanced(self):
        if self.advanced:
            self.filterImageButton.hide()
            self.lineLengthLabel.hide()
            self.lineLengthEdit.hide()
            self.sinPowerEdit.hide()
            self.sinPowerLabel.hide()
            self.thetaStepLabel.hide()
            self.thetaStepEdit.hide()
            self.deltaThLabel.hide()
            self.deltaThEdit.hide()
            self.minAreaLabel.hide()
            self.minAreaEdit.hide()
            self.advanced = False
        else:
            self.filterImageButton.show()
            self.lineLengthLabel.show()
            self.lineLengthEdit.show()
            self.sinPowerEdit.show()
            self.sinPowerLabel.show()
            self.thetaStepLabel.show()
            self.thetaStepEdit.show()
            self.deltaThLabel.show()
            self.deltaThEdit.show()
            self.minAreaLabel.show()
            self.minAreaEdit.show()
            self.advanced = True

    def updateConfig(self):
        tools.saveConfig(self)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Left:
            self.imageWidget.roi.moveLeft()
        elif key == QtCore.Qt.Key_Right:
            self.imageWidget.roi.moveRight()
        elif key == QtCore.Qt.Key_Up:
            self.imageWidget.roi.moveUp()
        elif key == QtCore.Qt.Key_Down:
            self.imageWidget.roi.moveDown()


class ImageWidget(pg.GraphicsLayoutWidget):

    def __init__(self, main, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main = main
        self.setWindowTitle('ImageGUI')
        self.subImgSize = 100

        # Item for displaying input image data
        self.inputVb = self.addViewBox(row=0, col=0)
        self.inputImg = pg.ImageItem()
        self.inputVb.addItem(self.inputImg)
        self.inputVb.setAspectLocked(True)
        self.thresBlockIm = pg.ImageItem()
        self.thresBlockIm.setZValue(10)  # make sure this image is on top
        self.thresBlockIm.setOpacity(0.5)
        self.inputVb.addItem(self.thresBlockIm)
        self.thresIm = pg.ImageItem()
        self.thresIm.setZValue(20)  # make sure this image is on top
        self.thresIm.setOpacity(0.5)
        self.inputVb.addItem(self.thresIm)

        # Contrast/color control
        self.inputImgHist = pg.HistogramLUTItem()
        self.inputImgHist.gradient.loadPreset('thermal')
        self.inputImgHist.setImageItem(self.inputImg)
        self.inputImgHist.vb.setLimits(yMin=0, yMax=20000)
        self.addItem(self.inputImgHist, row=0, col=1)

        # subimg
        self.subImg = pg.ImageItem()
        subimgHist = pg.HistogramLUTItem(image=self.subImg)
        subimgHist.gradient.loadPreset('thermal')
        self.addItem(subimgHist, row=1, col=1)

        self.subImgPlot = pg.PlotItem()
        self.subImgPlot.addItem(self.subImg)
        self.subImgPlot.hideAxis('left')
        self.subImgPlot.hideAxis('bottom')
        self.addItem(self.subImgPlot, row=1, col=0)

        # Custom ROI for selecting an image region
        pxSize = np.float(self.main.STEDPxEdit.text())
        self.roi = pyqtsub.SubImgROI(self.main.subImgSize/pxSize)
        self.inputVb.addItem(self.roi)
        self.roi.setZValue(10)  # make sure ROI is drawn above image
        self.roi.setOpacity(0.5)

        # Load sample STED image
        folder = os.path.join(os.getcwd(), 'ringfinder')
        if os.path.exists(folder):
            self.folder = folder
            self.loadSTED(os.path.join(folder, 'spectrinSTED.tif'))
        else:
            self.folder = os.getcwd()
            self.loadSTED(os.path.join(os.getcwd(), 'spectrinSTED.tif'))

        # Correlation
        self.pCorr = pg.PlotItem(labels={'left': ('Pearson coefficient'),
                                         'bottom': ('Angle', 'deg')})
        self.pCorr.showGrid(x=True, y=True)
        self.addItem(self.pCorr, row=0, col=2)

        # Optimal correlation visualization
        self.vb4 = self.addViewBox(row=1, col=2)
        self.img1 = pg.ImageItem()
        self.img2 = pg.ImageItem()
        self.vb4.addItem(self.img1)
        self.vb4.addItem(self.img2)
        self.img2.setZValue(10)  # make sure this image is on top
        self.img2.setOpacity(0.5)
        self.vb4.setAspectLocked(True)
        overlay_hist = pg.HistogramLUTItem()
        overlay_hist.gradient.loadPreset('thermal')
        overlay_hist.setImageItem(self.img2)
        overlay_hist.setImageItem(self.img1)
        self.addItem(overlay_hist, row=1, col=3)

        self.roi.sigRegionChanged.connect(self.updatePlot)

        self.ci.layout.setRowFixedHeight(0, 400)
        self.ci.layout.setRowFixedHeight(1, 400)
        self.ci.layout.setColumnFixedWidth(0, 400)
        self.ci.layout.setColumnFixedWidth(2, 400)

    def loadImage(self, tech, pxSize, crop=0, filename=None):

        try:

            if not(isinstance(filename, str)):
                filetypes = ('Tiff file', '*.tif;*.tiff')
                self.filename = utils.getFilename('Load ' + tech + ' image',
                                                  [filetypes], self.folder)
            else:
                self.filename = filename

            if self.filename is not None:

                self.folder = os.path.split(self.filename)[0]
                self.pxSize = pxSize
                self.inputVb.clear()

                # Image loading
                im = Image.open(self.filename)
                self.inputData = np.array(im).astype(np.float64)
                self.shape = self.inputData.shape
                self.inputData = self.inputData[crop:self.shape[0] - crop,
                                                crop:self.shape[1] - crop]
                self.shape = self.inputData.shape

                # We need 1um n-sized subimages
                self.subimgPxSize = int(np.round(1000/self.pxSize))
                self.n = (np.array(self.shape)/self.subimgPxSize).astype(int)

                # If n*subimgPxSize < shape, we crop the image
                self.remanent = np.array(self.shape) - self.n*self.subimgPxSize
                self.inputData = self.inputData[:self.n[0]*self.subimgPxSize,
                                                :self.n[1]*self.subimgPxSize]
                self.shape = self.inputData.shape

                self.nblocks = np.array(self.inputData.shape)/self.n
                self.blocksInput = tools.blockshaped(self.inputData,
                                                     *self.nblocks)

                self.showIm = np.fliplr(np.transpose(self.inputData))

                # Image plotting
                self.inputImg = pg.ImageItem()
                self.inputVb.addItem(self.inputImg)
                self.inputVb.setAspectLocked(True)
                self.inputImg.setImage(self.showIm)
                self.inputImgHist.setImageItem(self.inputImg)
                self.addItem(self.inputImgHist, row=0, col=1)
                self.inputVb.addItem(self.roi)
                self.inputVb.addItem(self.thresBlockIm)
                self.inputVb.addItem(self.thresIm)

                self.updateMasks()

                self.grid = pyqtsub.Grid(self.inputVb, self.shape, self.n)

                self.inputVb.setLimits(xMin=-0.05*self.shape[0],
                                       xMax=1.05*self.shape[0], minXRange=4,
                                       yMin=-0.05*self.shape[1],
                                       yMax=1.05*self.shape[1], minYRange=4)

                self.updateROI()
                self.updatePlot()

                return True

            else:
                return False

        except OSError:
            print('No file selected!')

    def loadSTED(self, filename=None):
        prevSigma = self.main.sigmaEdit.text()
        prevThres = self.main.intThresEdit.text()
        load = self.loadImage('STED', np.float(self.main.STEDPxEdit.text()),
                              filename=filename)
        if not(load):
            self.main.sigmaEdit.setText(prevSigma)
            self.main.intThresEdit.setText(prevThres)

    def loadSTORM(self, filename=None):
        prevSigma = self.main.sigmaEdit.text()
        prevThres = self.main.intThresEdit.text()
        self.inputImgHist.setLevels(0, 3)
        # The STORM image has black borders because it's not possible to
        # localize molecules near the edge of the widefield image.
        # Therefore we need to crop those 3px borders before running the
        # analysis.
        mag = np.float(self.main.magnificationEdit.text())
        load = self.loadImage('STORM', np.float(self.main.STORMPxEdit.text()),
                              crop=int(3*mag), filename=filename)
        if not(load):
            self.main.sigmaEdit.setText(prevSigma)
            self.main.intThresEdit.setText(prevThres)

    def updateMasks(self):
        """Binarization of image. """

        self.gaussSigma = np.float(self.main.sigmaEdit.text())/self.pxSize
        thr = np.float(self.main.intThresEdit.text())

        if self.main.testData:
            self.blocksInputS = [ndi.gaussian_filter(b, self.gaussSigma)
                                 for b in self.blocksInput]
            self.blocksInputS = np.array(self.blocksInputS)
            self.meanS = np.mean(self.blocksInputS, (1, 2))
            self.stdS = np.std(self.blocksInputS, (1, 2))
            thresholds = self.meanS + thr*self.stdS
            thresholds = thresholds.reshape(np.prod(self.n), 1, 1)
            mask = self.blocksInputS < thresholds
            self.blocksMask = np.array([bI < np.mean(bI) + thr*np.std(bI)
                                       for bI in self.blocksInputS])

            self.mask = tools.unblockshaped(mask, *self.inputData.shape)
            self.inputDataS = tools.unblockshaped(self.blocksInputS,
                                                  *self.shape)
        else:
            self.inputDataS = ndi.gaussian_filter(self.inputData,
                                                  self.gaussSigma)
            self.blocksInputS = tools.blockshaped(self.inputDataS,
                                                  *self.nblocks)
            self.meanS = np.mean(self.inputDataS)
            self.stdS = np.std(self.inputDataS)
            self.mask = self.inputDataS < self.meanS + thr*self.stdS
            self.blocksMask = tools.blockshaped(self.mask, *self.nblocks)

        self.showImS = np.fliplr(np.transpose(self.inputDataS))
        self.showMask = np.fliplr(np.transpose(self.mask))

        self.selectedMask = self.roi.getArrayRegion(self.showMask,
                                                    self.inputImg).astype(bool)

    def updatePlot(self):

        self.subImgPlot.clear()

        self.selected = self.roi.getArrayRegion(self.showIm, self.inputImg)
        self.selected = self.selected[1:-1, 1:-1]
        self.selectedS = self.roi.getArrayRegion(self.showImS, self.inputImg)
        self.selectedS = self.selectedS[1:-1, 1:-1]
        self.selectedMask = self.roi.getArrayRegion(self.showMask,
                                                    self.inputImg).astype(bool)
        self.selectedMask = self.selectedMask[1:-1, 1:-1]

        self.selectedMean = np.mean(self.selectedS)
        self.selectedStd = np.std(self.selectedS)

        shape = self.selected.shape
        self.subImgSize = shape[0]
        self.subImg.setImage(self.selected)
        self.subImgPlot.addItem(self.subImg)
        self.subImgPlot.vb.setLimits(xMin=-0.05*shape[0], xMax=1.05*shape[0],
                                     yMin=-0.05*shape[1], yMax=1.05*shape[1],
                                     minXRange=4, minYRange=4)
        self.subImgPlot.vb.setRange(xRange=(0, shape[0]), yRange=(0, shape[1]))

    def updateROI(self):
        self.roiSize = np.float(self.main.roiSizeEdit.text()) / self.pxSize
        self.roi.setSize(self.roiSize, self.roiSize)
        self.roi.step = int(self.shape[0]/self.n[0])
        self.roi.keyPos = (0, 0)

    def corrMethodGUI(self):

        self.pCorr.clear()

        # We apply intensity threshold to smoothed data so we don't catch
        # tiny bright spots outside neurons
        thr = np.float(self.main.intThresEdit.text())
        if np.any(self.selectedS > self.selectedMean + thr*self.selectedStd):

            self.getDirection()

            # we apply the correlation method for ring finding for the
            # selected subimg
            minLen = np.float(self.main.lineLengthEdit.text()) / self.pxSize
            thStep = np.float(self.main.thetaStepEdit.text())
            deltaTh = np.float(self.main.deltaThEdit.text())
            wvlen = np.float(self.main.wvlenEdit.text()) / self.pxSize
            sinPow = np.float(self.main.sinPowerEdit.text())
            args = [self.selectedMask, minLen, thStep, deltaTh, wvlen, sinPow]
            output = tools.corrMethod(self.selected, *args, developer=True)
            self.th0, corrTheta, corrMax, thetaMax, phaseMax = output

            if np.all([self.th0, corrMax]) is not None:
                self.bestAxon = simAxon(imSize=self.subImgSize, wvlen=wvlen,
                                        theta=thetaMax, phase=phaseMax,
                                        b=sinPow).data
                self.bestAxon = np.ma.array(self.bestAxon,
                                            mask=self.selectedMask,
                                            fill_value=0)
                self.img1.setImage(self.bestAxon.filled(0))
                self.img2.setImage(self.selected)

                shape = self.selected.shape
                self.vb4.setLimits(xMin=-0.05*shape[0], xMax=1.05*shape[0],
                                   yMin=-0.05*shape[1], yMax=1.05*shape[1],
                                   minXRange=4, minYRange=4)
                self.vb4.setRange(xRange=(0, shape[0]), yRange=(0, shape[1]))

                # plot the threshold of correlation chosen by the user
                # phase steps are set to 20, TO DO: explore this parameter
                theta = np.arange(np.min([self.th0 - deltaTh, 0]), 180, thStep)
                pen1 = pg.mkPen(color=(0, 255, 100), width=2,
                                style=QtCore.Qt.SolidLine, antialias=True)
                self.pCorr.plot(theta, corrTheta, pen=pen1)

                # plot the area within deltaTh from the found direction
                if self.th0 is not None:
                    thArea = np.arange(self.th0 - deltaTh, self.th0 + deltaTh)
                    if self.th0 < 0:
                        thArea += 180
                    gap = 0.05*(np.max(corrTheta) - np.min(corrTheta))
                    brushMax = np.max(corrTheta)*np.ones(len(thArea)) + gap
                    brushMin = np.min(corrTheta) - gap
                    self.pCorr.plot(thArea, brushMax, fillLevel=brushMin,
                                    fillBrush=(50, 50, 200, 100), pen=None)

            corrThres = np.float(self.main.corrThresEdit.text())
            rings = corrMax > corrThres
            if rings and np.abs(self.th0 - thetaMax) <= deltaTh:
                self.main.resultLabel.setText('<strong>MY PRECIOUS!<\strong>')
            else:
                if rings:
                    print('Correlation maximum outside direction theta range')
                self.main.resultLabel.setText('<strong>No rings<\strong>')
        else:
            print('Data below intensity threshold')
            self.main.resultLabel.setText('<strong>No rings<\strong>')

    def intThreshold(self):

        if self.main.intThrButton.isChecked():

            neuron = np.zeros(len(self.blocksInput))
            thr = np.float(self.main.intThresEdit.text())

            # Find neurons above background
            thres = self.meanS + thr*self.stdS
            if not(self.main.testData):
                thres = thres*np.ones(self.blocksInput.shape)
            neuronTh = np.array([np.any(self.blocksInputS[i] > thres[i])
                                 for i in np.arange(len(self.blocksInputS))])

            # Find sufficintly filled subimages
            minArea = 0.01*float(self.main.minAreaEdit.text())
            neuronFrac = np.array([1 - np.sum(m)/np.size(m) > minArea
                                   for m in self.blocksMask])

            neuron = neuronTh * neuronFrac

            # code for visualization of the output
            neuron = neuron.reshape(*self.n)
            neuron = np.repeat(neuron, self.inputData.shape[0]/self.n[0], 0)
            neuron = np.repeat(neuron, self.inputData.shape[1]/self.n[1], 1)
            showIm = np.fliplr(np.transpose(neuron))
            self.thresBlockIm.setImage(100*showIm.astype(float))
            self.thresIm.setImage(100*self.showMask.astype(float))

        else:
            self.thresBlockIm.clear()
            self.thresIm.clear()

    def imageFilter(self):
        ''' Removes background data from image.'''

        im = np.fliplr(np.transpose(self.inputData * np.invert(self.mask)))
        self.inputImg.setImage(im)

    def getDirection(self):

        minLen = np.float(self.main.lineLengthEdit.text()) / self.pxSize
        self.th0, lines = tools.getDirection(self.selected,
                                             np.invert(self.selectedMask),
                                             minLen, True)

        # Lines plot
        pen = pg.mkPen(color=(0, 255, 100), width=1, style=QtCore.Qt.SolidLine,
                       antialias=True)
        for line in lines:
            p0, p1 = line
            self.subImgPlot.plot((p0[1], p1[1]), (p0[0], p1[0]), pen=pen)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = GollumDeveloper()
    win.show()
    app.exec_()
