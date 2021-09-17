'''
model = new parser (lista de archivos fuente).build()
ifc_model = new IFC_generator(model).generate() // pag 81 creational patterns
drawingScaleFactor = sys.argv[2]
if len(sys.argv) < 2:
    print('Falta un argumento --> please set drawingScaleFactor')
    exit(0)
drawingScaleFactor = 13.2
'''
import sys , os
import uuid
import time
import tempfile
import ifcopenshell
import faulthandler; faulthandler.enable()
# FREECADPATH = '/usr/lib/freecad-python3/lib'
# sys.path.append(FREECADPATH)
# from FreeCAD import Vector





#Dev Classes imports
from Parser import *
from BuildingElement import *
from ColumnBuildingElement import *
from SlabBuildingElement import *
from BeamBuildingElement import *
from StoreyBuildingElement import *


         
class IfcModelGenerator:
    def __init__(self,parser):
        self.O = 0., 0., 0.
        self.X = 1., 0., 0.
        self.Y = 0., 1., 0.
        self.Z = 0., 0., 1.
        self.parser=parser
        self.filename=""
        self.template=""
        self.temp_filename=""
        self.GUI=""
        self.owner_history=""
        self.project=""
        self.context=""
        self.storey_placement=""
        self.ifcfile=None        
        
    def createGlobalUniqueId(self):
    	self.GUI=ifcopenshell.guid.compress(uuid.uuid1().hex)
    	
    def getGUId(self):
    	return self.GUI
   
    def getLevelNr(self):
        return self.parser.getLevelNr()

    def getLevelsData(self):
        return self.parser.getLevelsData()
        
    def setTripleCartesian(self,O = (0., 0., 0.),X = (1., 0., 0.),Y = (0., 1., 0.), Z = (0., 0., 1.)):
        self.O = O
        self.X = X
        self.Y = Y
        self.Z = Z
        

    def buildHeaderTemplateIfcModel(self):
        '''A template IFC file to quickly populate entity instances for an IfcProject with its dependencies'''
        timestamp = time.time()
        timestring = time.strftime("%Y%m%d-%H_%M_%S", time.gmtime(timestamp))
        filename=self.filename
        creator = "Martin Urbieta"
        organization = "LIFIA"
        application, application_version = "IfcOpenShell", "0.5"
        self.createGlobalUniqueId()
        guid=self.getGUId()
        project_globalid, project_name = guid, "Hello Bim"
                            
        template = """ISO-10303-21;
        HEADER;
        FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
        FILE_NAME('%(filename)s','%(timestring)s',('%(creator)s'),('%(organization)s'),'%(application)s','%(application)s','');
        FILE_SCHEMA(('IFC2X3'));
        ENDSEC;
        DATA;
        #1=IFCPERSON($,$,'%(creator)s',$,$,$,$,$);
        #2=IFCORGANIZATION($,'%(organization)s',$,$,$);
        #3=IFCPERSONANDORGANIZATION(#1,#2,$);
        #4=IFCAPPLICATION(#2,'%(application_version)s','%(application)s','');
        #5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,%(timestamp)s);
        #6=IFCDIRECTION((1.,0.,0.));
        #7=IFCDIRECTION((0.,0.,1.));
        #8=IFCCARTESIANPOINT((0.,0.,0.));
        #9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
        #10=IFCDIRECTION((0.,1.,0.));
        #11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#9,#10);
        #12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
        #13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
        #14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
        #15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
        #16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
        #17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
        #18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
        #19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
        #20=IFCPROJECT('%(project_globalid)s',#5,'%(project_name)s',$,$,$,$,(#11),#19);
        ENDSEC;
        END-ISO-10303-21;
        """ % locals()
        self.template=template
        
    def makeIfcFile(self):
        '''Write the template to a temporary file'''
        temp_handle, self.temp_filename = tempfile.mkstemp(suffix=".ifc")
        with open(self.temp_filename, "w") as f:
            f.write(self.template)
 
    def getTempFilename(self):
    	return self.temp_filename

    def openIfcFile(self):
    	if self.ifcfile is None:
    		pathTempFilename= self.getTempFilename()
    		self.ifcfile= ifcopenshell.open(pathTempFilename)
    		
    def getIfcFile(self):
    	return self.ifcfile  		
	
    def getOwnerHistory(self):
    	return self.owner_history

    def getProject(self):
    	return self.project
    
    def getContext(self):
    	return self.context
    	
    def getIfcColumns(self):
    	cList=self.ifcfile.by_type("IfcColumn")
    	return cList 
    	
    def getIfcBeams(self):
    	bList= self.ifcfile.by_type("IfcBeam")
    	return bList
    	
    def getIfcSlabs(self):
    	sList=self.ifcfile.by_type("IfcSlab")
    	return sList
    	
    def getIfcFileReferences(self):
    	self.owner_history=self.ifcfile.by_type("IfcOwnerHistory")[0]
    	self.project=self.ifcfile.by_type("IfcProject")[0]
    	self.context=self.ifcfile.by_type("IfcGeometricRepresentationContext")[0]
      
    def getStoreyPlacement(self):
    	return self.storey_placement
    	    
    def setNameIfcModel(self,filePrefixName="IFC_model_"):
        timestamp = time.time()
        timestring = time.strftime("%Y%m%d-%H_%M_%S", time.gmtime(timestamp))
        self.filename = filePrefixName+timestring+".ifc"
    
    def saveIfcModel(self):
        self.getIfcFile().write(self.filename)
        print('File Saved!\n\n')
    
    def columnsProcessParser(self,columnsIndex,zFloor,building_storey,height):
        for column in columnsIndex:
            #print(column)
            tag = column['tag']
            cx = column['cx']
            cy = column['cy']
            bx = column['bx']
            by = column['by']
            cz=zFloor
            col = Column(self,building_storey,cx,cy,cz-height,bx,by,height,tag)
            col.builder()

    def slabsProcessParser(self,slabsIndex,building_storey,zFloor):
        for slab in slabsIndex:
            tag = slab['tag']
            cx = slab['cx']
            cy = slab['cy']
            bx = slab['bx']
            by = slab['by']
            height = slab['height']
            slab = Slab(self,building_storey,cx,cy,zFloor,bx,by,height,tag)
            slab.builder()

    def beamsProcessParser(self,beamsIndex,building_storey,zFloor):
        for beam in beamsIndex:
            tag = beam['tag']
            cxi = beam['data']['cx']
            cyi = beam['data']['cy']
            wBeam = beam['data']['width']
            hBeam = beam['data']['height']
            lBeam = beam['data']['lenght']
            vBeam = beam['data']['direction']
            AreaProfile=""
            position=(cxi,cyi,zFloor)
            beamConst = Beam(self,building_storey,tag,AreaProfile,lBeam ,position,vBeam)
            beamConst.AreaProfile=beamConst.Rect_Section(wBeam,hBeam)
            beamConst.builder()
       
    def processParser(self):
        zFloor=0.0
        cz=0.0
        levelNr=self.getLevelNr()
        columnsIndex= []
        beamsIndex= []
        slabsIndex= []
        #print('levels nr',levelNr)
        levelsData=self.getLevelsData()
        #print('levelsdata:',levelsData)
        for i in range(levelNr):
            height= float(levelsData[i][0])
            columnsIndex= levelsData[i][1]
            beamsIndex= levelsData[i][2]
            slabsIndex= levelsData[i][3]
            #print('IndexCol:',columnsIndex)
            #print('zFloor:',zFloor)
            storey = Storey(self,zFloor)
            #print('storey',"|",storey.elevation,"|",storey.ifcModelGenerator,"|")
            storey.buildHierarchy()
            zFloor=zFloor+height

    		#print('i:',i)
            building_storey = self.ifcfile.by_type("IfcBuildingStorey")[i]
            
            self.columnsProcessParser(columnsIndex,zFloor,building_storey,height)
            self.slabsProcessParser(slabsIndex,building_storey,zFloor)
            self.beamsProcessParser(beamsIndex,building_storey,zFloor)
     
    def builder(self):
    	self.setNameIfcModel('POO_IFC_model_')
    	self.buildHeaderTemplateIfcModel()
    	self.makeIfcFile()
    	self.openIfcFile()
    	self.getIfcFileReferences()
    	self.processParser()
    	self.saveIfcModel()