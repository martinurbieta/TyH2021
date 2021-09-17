import sys , os
from os import listdir
from os.path import isfile, join
import ast
import json
import pandas as pd

class Parser:
    def __init__(self,predictionsFolder = 'predicciones',relatedFolder='relacionados'):
        self.levelsData=[]
        script_dir= os.path.dirname(os.path.realpath("__file__"))
        self.predictionsPath= os.path.join(script_dir, predictionsFolder)
        self.relatedPath= os.path.join(script_dir, relatedFolder)
        
        predictionsFilesList= os.listdir(self.predictionsPath)
        predictionsFilesList.sort()
        self.predictionsFilesList=predictionsFilesList
        
        relatedFilesList= os.listdir(self.relatedPath)
        relatedFilesList.sort()
        self.relatedFilesList=relatedFilesList
        self.totalLevels=0
        self.levelNr =0
        self.heightlist=[]
        self.filennr = 0
        self.number_files = len(self.predictionsFilesList)
        self.columnsIndex = []
        self.beamsIndex = []
        self.beamsIndexRel = []
        self.slabsIndex = []
        self.nCol=0
        self.hCol=0
    def getLevelNr(self):
        return self.levelNr

    def getLevelsData(self):
        return self.levelsData
        

    def parsePredictionFile(self):
        for self.filennr in range(self.number_files):
            print('base file to load:      '+self.predictionsFilesList[self.filennr],' - File order:',self.filennr+1,'/',self.number_files)

            #Read one file of input folder.

            predictionFile = open(self.predictionsPath+'/'+self.predictionsFilesList[self.filennr], 'r')

            lines = predictionFile.readlines()





            for line in lines:
                eval_line = ast.literal_eval(line)
                if eval_line['elem']=='column':
                    tag = str(eval_line['tag'])
                    y1 =float(eval_line['points']['y1'])
                    y2 =float(eval_line['points']['y2'])
                    x1 =float(eval_line['points']['x1'])
                    x2 =float(eval_line['points']['x2'])
                    cx =round( ((x2+x1)/2),2)
                    cy =round( ((y2+y1)/2),2)
                    bx =round( pow((pow(x2-x1,2)),0.5),2)
                    by = round(pow((pow(y2-y1,2)),0.5),2)
                    self.columnsIndex.append({'tag':tag,'cx':cx,'cy':cy,'bx':bx,'by':by})

            for line in lines:
                eval_line = ast.literal_eval(line)
                if eval_line['elem']=='slab':
                    tag = str(eval_line['tag'])
                    y1 =float(eval_line['points']['y1'])
                    y2 =float(eval_line['points']['y2'])
                    x1 =float(eval_line['points']['x1'])
                    x2 =float(eval_line['points']['x2'])
                    cx =round( ((x2+x1)/2),2)
                    cy =round( ((y2+y1)/2),2)
                    bx =round( pow((pow(x2-x1,2)),0.5),2)
                    by = round(pow((pow(y2-y1,2)),0.5),2)
                    height = round(min(bx,by)/30,2) # cross slab , simple supported.
                    self.slabsIndex.append({'tag':tag,'cx':cx,'cy':cy,'bx':bx,'by':by,'height':height})

            predictionFile.close()
    def parseRelacionadosFile(self):
    ##Beams length has to be corrected related column's center.
        relatedPredictionsFile = open(self.relatedPath+'/'+self.relatedFilesList[self.filennr], 'r')
        print('related file to load:      '+self.relatedFilesList[self.filennr],' - File order:',self.filennr+1,'/',self.number_files)
        lines = relatedPredictionsFile.readlines()

        lines=str(lines).replace('"','')
        lines=str(lines).replace('\\n','')
        lines=ast.literal_eval(lines)
        for data in lines:

            try:
                if len(data['relItems'])>=2:
                    beamTag=data['tag']
                    bx1=float(data['points']['x1'])
                    bx2=float(data['points']['x2'])
                    by1=float(data['points']['y1'])
                    by2=float(data['points']['y2'])
                    y1 =float(data['relItems'][0]['points']['y1'])
                    x1 =float(data['relItems'][0]['points']['x1'])
                    y2 =float(data['relItems'][0]['points']['y2'])
                    x2 =float(data['relItems'][0]['points']['x2'])
                    y3 =float(data['relItems'][1]['points']['y1'])
                    x3 =float(data['relItems'][1]['points']['x1'])
                    y4 =float(data['relItems'][1]['points']['y2'])
                    x4 =float(data['relItems'][1]['points']['x2'])
                    cxi =round( ((x1+x2)/2),2)
                    cyi =round( ((y1+y2)/2),2)
                    cxj =round( ((x3+x4)/2),2)
                    cyj =round( ((y3+y4)/2),2)
                    dbx =round( pow((pow(bx2-bx1,2)),0.5),2)
                    dby = round(pow((pow(by2-by1,2)),0.5),2)
                    lBeam= pow(pow(cxj-cxi,2)+pow(cyj-cyi,2),0.5)
                    lBeam= round(lBeam,2)
                    #lBeam = max(dx,dy)
                    wBeam = min(dbx,dby)
                    hBeam = round(lBeam/10,2) 
                    vx = cxj-cxi
                    vy = cyj-cyi
                    vBeam=(vx,vy,0.0)
                    self.beamsIndex.append({'tag':beamTag,'data':{'cx':cxi,'cy':cyi,'width':wBeam,'height':hBeam,'lenght':lBeam,'direction':vBeam}})
            except:
                print('file line doesnt fit with readable structure')
                #exit(0)
        relatedPredictionsFile.close()

    def columnsHeightEstimation(self):
        # Estimate columns general height.
        mWidthCol=0
        nCol=0

        for col in self.columnsIndex:
            bx = col['bx']

            by = col['by']
            bm = (bx+by)/2
            mWidthCol=mWidthCol+bm
            nCol=nCol+1
        self.nCol=len(self.columnsIndex)
        self.hCol=round((mWidthCol/nCol)*13,2)  #13 defined as 2.6m/0.2m=13 (h/dimCol)
        self.heightlist.append(self.hCol)
        #print('column height',self.hCol)

        newLevel=[]
        newLevel=[self.hCol,self.columnsIndex,self.beamsIndex,self.slabsIndex]
        #levelsData.append({'level':self.levelNr,'data':newLevel})
        self.levelsData.append(newLevel)
        self.totalLevels=self.totalLevels+1

        self.levelNr = self.levelNr+1
            
    def build(self):
        self.parsePredictionFile()
        self.parseRelacionadosFile()
        self.columnsHeightEstimation()