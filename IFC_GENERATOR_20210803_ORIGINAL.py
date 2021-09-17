#!/usr/bin/env python
# coding: utf-8

# # CREATING IFC FILE FROM PLANS RECOGNITION

# ## 1.- PROCESS PREDICCIONES FILES AND RELATED OBJECTS OUTPUT

# ### distance.py relates the prediction file with pivot on column or beam. A proximity parameter must be set.

# ### on terminal:  
# <b>python3 distance.py 'pred_EDF 03 - EST-06.txt' 30 beam column</b>

# se recibe archivo 
# <b>relacionados0.txt</b>

# In[17]:


import sys , os
import uuid
import time
import tempfile
import ifcopenshell
FREECADPATH = '/usr/lib/freecad-python3/lib'
sys.path.append(FREECADPATH)
from FreeCAD import Vector
from os import listdir
from os.path import isfile, join
import ast
import json
import pandas as pd

    ############ READING INPUT ################

## Create a list of files in folder for input reading.
predictionsPath = "/home/martinurbieta/develp/script/productos/20210803/predicciones/"
predictionFilesList = os.listdir(predictionsPath)
predictionFilesList.sort()

relatedPredictionsPath = "/home/martinurbieta/develp/script/productos/20210803/relacionados/"
relatedPredictionsFilesList = os.listdir(relatedPredictionsPath)
relatedPredictionsFilesList.sort()

print(predictionFilesList)

#count pair of files in folder.

listFiles = os.listdir(predictionsPath) # dir is your directory path
number_files = len(listFiles)
filenr = 0
totalLevels = 0
levelNr =0
levelsData=[]
hColList =[]
for filenr in range(number_files):
    print('base file to load:      '+predictionFilesList[filenr],' - File order:',filenr+1,'/',number_files)

    #Read one file of input folder.

    predictionFile = open(predictionsPath+'/'+predictionFilesList[filenr], 'r')

    lines = predictionFile.readlines()

    columnsIndex = []
    beamsIndex = []
    beamsIndexRel = []
    slabsIndex = []
    heightList =[]
    nCol=0
    hCol=0
    

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
            columnsIndex.append({'tag':tag,'cx':cx,'cy':cy,'bx':bx,'by':by})

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
            eSlab = round(min(bx,by)/30,2) # cross slab , simple supported.
            slabsIndex.append({'tag':tag,'cx':cx,'cy':cy,'bx':bx,'by':by,'hSlab':eSlab})




    '''
    for line in lines:
        eval_line = ast.literal_eval(line)
        if eval_line['elem']=='beam':
            tag = str(eval_line['tag'])
            y1 =float(eval_line['points']['y1'])
            y2 =float(eval_line['points']['y2'])
            y3 =float(eval_line['points']['y1'])
            y4 =float(eval_line['points']['y2'])
            x1 =float(eval_line['points']['x1'])
            x2 =float(eval_line['points']['x2'])
            x3 =float(eval_line['points']['x2'])
            x4 =float(eval_line['points']['x1'])
            cxi =round( ((x1+x4)/2),2)
            cyi =round( ((y1+y4)/2),2)
            cxj =round( ((x2+x3)/2),2)
            cyj =round( ((y2+y3)/2),2)
            dx =round( pow((pow(x2-x1,2)),0.5),2)
            dy = round(pow((pow(y2-y1,2)),0.5),2)
            lBeam = max(dx,dy)
            wBeam = min(dx,dy)
            hBeam = round(lBeam/10,2) 
            vx = cxj-cxi
            vy = cyj-cyi
            vBeam=(vx,vy,0.0)
            beamsIndex.append({'tag':tag,'data':{'cx':cxi,'cy':cyi,'width':wBeam,'height':hBeam,'lenght':lBeam,'direction':vBeam}})
    ''' 
    predictionFile.close()

    ##Beams length has to be corrected related column's center.
    relatedPredictionsFile = open(relatedPredictionsPath+'/'+relatedPredictionsFilesList[filenr], 'r')
    print('related file to load:      '+relatedPredictionsFilesList[filenr],' - File order:',filenr+1,'/',number_files)
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
                beamsIndex.append({'tag':beamTag,'data':{'cx':cxi,'cy':cyi,'width':wBeam,'height':hBeam,'lenght':lBeam,'direction':vBeam}})
        except:
            print('file line doesnt fit with readable structure')
            #exit(0)

    # Estimate columns general height.
    nCol=0
    
    for col in columnsIndex:
        bx = col['bx']
        
        by = col['bx']
        bm = (bx+by)/2
        hCol=hCol+bm
        nCol=nCol+1
    nCol=len(columnsIndex)

    hCol=round((hCol/nCol)*13,2)  #13 defined as 2.6m/0.2m=13 (h/dimCol)
    hColList.append(hCol)
    
    newLevel=[]
    newLevel=[hCol,columnsIndex,beamsIndex,slabsIndex]
    #levelsData.append({'level':levelNr,'data':newLevel})
    levelsData.append(newLevel)
    totalLevels=totalLevels+1

    levelNr = levelNr+1
    predictionFile.close()
    


O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.

column_bx = 0.2    
column_by = 0.2
column_h = 3.3

cx = 0.0    
cy = 0.0
cz = 0.0

# Helper function definitions

# Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples
def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

# Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement
def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile,point,dir1,dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
    return ifclocalplacement2

# Creates an IfcPolyLine from a list of points, specified as Python tuples
def create_ifcpolyline(ifcfile, point_list):
    ifcpts = []
    for point in point_list:
        point = ifcfile.createIfcCartesianPoint(point)
        ifcpts.append(point)
    polyline = ifcfile.createIfcPolyLine(ifcpts)
    return polyline
    
# Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples
def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = create_ifcpolyline(ifcfile, point_list)
    ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = ifcfile.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid
    
create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

########################### BEAM EXAMPLE ########################################################

def create_ifcBeam(ifcFile ,Container, Name , section , L , position , direction):
    Z = 0.,0.,1.
    beam = ifcFile.createIfcBeam(create_guid(),owner_history , Name)
    beam.ObjectType ='beam'
    
    beam_Point =ifcFile.createIfcCartesianPoint ( position ) 
    beam_Axis2Placement = ifcFile.createIfcAxis2Placement3D(beam_Point)
    beam_Axis2Placement.Axis = ifcFile.createIfcDirection(direction)
    beam_Axis2Placement.RefDirection =ifcFile.createIfcDirection(Vector(direction).cross(Vector(Z)))

    beam_Placement = ifcFile.createIfcLocalPlacement(Container.ObjectPlacement,beam_Axis2Placement)
    beam.ObjectPlacement=beam_Placement

    beam_ExtrudePlacement = ifcFile.createIfcAxis2Placement3D(ifcFile.createIfcCartesianPoint ( (0.,0.,0.) )   )
   
    beam_Extruded=ifcFile.createIfcExtrudedAreaSolid()
    beam_Extruded.SweptArea=section
    beam_Extruded.Position=beam_ExtrudePlacement
    beam_Extruded.ExtrudedDirection = ifcFile.createIfcDirection(Z)
    beam_Extruded.Depth = L
    
    beam_Repr=ifcFile.createIfcShapeRepresentation()
    beam_Repr.ContextOfItems=context
    beam_Repr.RepresentationIdentifier = 'Body'
    beam_Repr.RepresentationType = 'SweptSolid'
    beam_Repr.Items = [beam_Extruded]
    
    beam_DefShape=ifcFile.createIfcProductDefinitionShape()
    beam_DefShape.Representations=[beam_Repr]
    beam.Representation=beam_DefShape
    
    Flr1_Container = ifcFile.createIfcRelContainedInSpatialStructure(create_guid(),owner_history)
    Flr1_Container.RelatedElements=[beam]
    Flr1_Container.RelatingStructure= Container
    
        # Define and associate the column material
    material = ifcfile.createIfcMaterial("beam material")
    material_layer = ifcfile.createIfcMaterialLayer(material, L/200, None)
    material_layer_set = ifcfile.createIfcMaterialLayerSet([material_layer], None)
    material_layer_set_usage = ifcfile.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", -0.1)
    ifcfile.createIfcRelAssociatesMaterial(create_guid(), owner_history, RelatedObjects=[beam], RelatingMaterial=material_layer_set_usage)
    
# Create and assign property set
    property_values = [
        ifcfile.createIfcPropertySingleValue("Reference", "Reference", ifcfile.create_entity("IfcText", "Describe the Reference"), None),
        ifcfile.createIfcPropertySingleValue("IsExternal", "IsExternal", ifcfile.create_entity("IfcBoolean", True), None),
        ifcfile.createIfcPropertySingleValue("ThermalTransmittance", "ThermalTransmittance", ifcfile.create_entity("IfcReal", 2.569), None),
        ifcfile.createIfcPropertySingleValue("IntValue", "IntValue", ifcfile.create_entity("IfcInteger", 2), None)
    ]
    property_set = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Pset_BeamCommon", None, property_values)
    ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [beam], property_set)

    # Add quantity information
    quantity_values = [
        ifcfile.createIfcQuantityLength("Length", "Length of the beam", None, L),
 #       ifcfile.createIfcQuantityArea("Area", "Area of the cross section", None, beam_AreaProfile.XDim * beam_AreaProfile.YDim),
 #       ifcfile.createIfcQuantityVolume("Volume", "Volume of the column", None, beam_AreaProfile.XDim * beam_AreaProfile.YDim * L)
    ]
    element_quantity = ifcfile.createIfcElementQuantity(create_guid(), owner_history, "BaseQuantities", None, None, quantity_values)
    ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [beam], element_quantity)

    # Relate the window and wall to the building storey
    ifcfile.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, "Building Storey Container", None, [beam], building_storey)    
    
    

def I_Section(W ,D , tw , tf  , r):
    beam_Axis2Placement2D =ifcfile.createIfcAxis2Placement2D( 
                          ifcfile.createIfcCartesianPoint( (0.,0.) ) )
    
    beam_AreaProfile = ifcfile.createIfcIShapeProfileDef('AREA')
    beam_AreaProfile.Position = beam_Axis2Placement2D 
    beam_AreaProfile.OverallWidth = W
    beam_AreaProfile.OverallDepth = D
    beam_AreaProfile.WebThickness = tw
    beam_AreaProfile.FlangeThickness = tf
    beam_AreaProfile.FilletRadius=r
    return beam_AreaProfile

def L_Section(W ,D , t   , r):
    beam_Axis2Placement2D =ifcfile.createIfcAxis2Placement2D( 
                          ifcfile.createIfcCartesianPoint( (0.,0.) ) )
    
    beam_AreaProfile = ifcfile.createIfcLShapeProfileDef('AREA')
    beam_AreaProfile.Position = beam_Axis2Placement2D 
    beam_AreaProfile.Width = W
    beam_AreaProfile.Depth = D
    beam_AreaProfile.Thickness = t

    beam_AreaProfile.FilletRadius=r
    return beam_AreaProfile

def U_Section(W ,D , tw  , tf  , r):
    beam_Axis2Placement2D =ifcfile.createIfcAxis2Placement2D( 
                          ifcfile.createIfcCartesianPoint( (0.,0.) ) )
    
    beam_AreaProfile = ifcfile.createIfcUShapeProfileDef('AREA')
    beam_AreaProfile.Position = beam_Axis2Placement2D 
    beam_AreaProfile.FlangeWidth = W
    beam_AreaProfile.Depth = D
    beam_AreaProfile.WebThickness = tw
    beam_AreaProfile.FlangeThickness = tf
    beam_AreaProfile.FilletRadius=r
    beam_AreaProfile.EdgeRadius=r*0.5
    return beam_AreaProfile

def Rect_Section(b, h):
    beam_Axis2Placement2D =ifcfile.createIfcAxis2Placement2D( 
                          ifcfile.createIfcCartesianPoint( (0.,0.) ) )
    
    beam_AreaProfile = ifcfile.createIfcRectangleProfileDef('AREA')
    beam_AreaProfile.Position = beam_Axis2Placement2D 
    beam_AreaProfile.XDim = b
    beam_AreaProfile.YDim = h
    return beam_AreaProfile



########################### END BEAM EXAMPLE ########################################################




# IFC template creation

timestamp = time.time()
timestring = time.strftime("%Y%m%d-%H_%M_%S", time.gmtime(timestamp))
filename = "test_script_colBeamSlab_"+timestring+".ifc"
creator = "Martin Urbieta"
organization = "LIFIA"
application, application_version = "IfcOpenShell", "0.5"
project_globalid, project_name = create_guid(), "Hello Bim"
    
# A template IFC file to quickly populate entity instances for an IfcProject with its dependencies
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

# Write the template to a temporary file 
temp_handle, temp_filename = tempfile.mkstemp(suffix=".ifc")
with open(temp_filename, "w") as f:
    f.write(template)
 
# Obtain references to instances defined in template
ifcfile = ifcopenshell.open(temp_filename)
owner_history = ifcfile.by_type("IfcOwnerHistory")[0]
project = ifcfile.by_type("IfcProject")[0]
context = ifcfile.by_type("IfcGeometricRepresentationContext")[0]

# IFC hierarchy creation
site_placement = create_ifclocalplacement(ifcfile)
site = ifcfile.createIfcSite(create_guid(), owner_history, "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)

building_placement = create_ifclocalplacement(ifcfile, relative_to=site_placement)
building = ifcfile.createIfcBuilding(create_guid(), owner_history, 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)

storey_placement = create_ifclocalplacement(ifcfile, relative_to=building_placement)


heigthLevel=0
for i in range(levelNr):

    heigthLevel = heigthLevel+hColList[i]
    elevation = heigthLevel
    storeyName= str('Level_'+str(i))

    building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, storeyName, None, None, storey_placement, None, None, "ELEMENT", elevation)
    container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])

'''
elevation = 0.0
storeyName= 'GroundFloor'

building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, storeyName, None, None, storey_placement, None, None, "ELEMENT", elevation)
container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])


elevation = 6.0
storeyName= 'RoofTop'

building_storey = ifcfile.createIfcBuildingStorey(create_guid(), owner_history, storeyName, None, None, storey_placement, None, None, "ELEMENT", elevation)

container_storey = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, [building_storey])
'''
container_site = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
container_project = ifcfile.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])

# Column creation: Define the column shape as a polyline axis and an extruded area solid
# Input de dimensiones de elemento
def create_ifcColumn(ifcfile, cx=0,cy=0,cz=0, column_bx = 0.2, column_by = 0.2, column_h = 3.3,tagCol="aColumn"):

    column_placement = create_ifclocalplacement(ifcfile, relative_to=storey_placement)
    polyline = create_ifcpolyline(ifcfile, [(cx-0.5*column_bx, cy, cz), (cx+0.5*column_bx , cy, cz)])
    axis_representation = ifcfile.createIfcShapeRepresentation(context, "Axis", "Curve2D", [polyline])

    extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    point_list_extrusion_area = [(cx-0.5*column_bx, cy-column_by*0.5, cz), (cx+0.5*column_bx, cy-column_by*0.5, cz), (cx+column_bx*0.5, cy+column_by*0.5, cz), (cx-column_bx*0.5, cy+column_by*0.5, cz), (cx-0.5*column_bx, cy-column_by*0.5, cz)]
    solid = create_ifcextrudedareasolid(ifcfile, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), column_h)
    body_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])

    product_shape = ifcfile.createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])

    column = ifcfile.createIfcColumn(create_guid(), owner_history, "Columna", "Una columna increible", None, column_placement, product_shape, None)

    # Define and associate the column material
    material = ifcfile.createIfcMaterial("column material")
    material_layer = ifcfile.createIfcMaterialLayer(material, 0.2, None)
    material_layer_set = ifcfile.createIfcMaterialLayerSet([material_layer], None)
    material_layer_set_usage = ifcfile.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", -0.1)
    ifcfile.createIfcRelAssociatesMaterial(create_guid(), owner_history, RelatedObjects=[column], RelatingMaterial=material_layer_set_usage)

    # Create and assign property set
    property_values = [
        ifcfile.createIfcPropertySingleValue("Reference", "Reference", ifcfile.create_entity("IfcText", "Describe the Reference"), None),
        ifcfile.createIfcPropertySingleValue("IsExternal", "IsExternal", ifcfile.create_entity("IfcBoolean", True), None),
        ifcfile.createIfcPropertySingleValue("ThermalTransmittance", "ThermalTransmittance", ifcfile.create_entity("IfcReal", 2.569), None),
        ifcfile.createIfcPropertySingleValue("IntValue", "IntValue", ifcfile.create_entity("IfcInteger", 2), None)]
    property_set = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Pset_ColumnCommon", None, property_values)
    ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [column], property_set)

    # Add quantity information
    quantity_values = [
        ifcfile.createIfcQuantityLength("Length", "Length of the column", None, column_h),
        ifcfile.createIfcQuantityArea("Area", "Area of the cross section", None, column_bx * column_by),
        ifcfile.createIfcQuantityVolume("Volume", "Volume of the column", None, column_h * column_bx * column_by)]
    
    element_quantity = ifcfile.createIfcElementQuantity(create_guid(), owner_history, "BaseQuantities", None, None, quantity_values)
    ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [column], element_quantity)

    # Relate the window and wall to the building storey
    ifcfile.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, "Building Storey Container", None, [column], building_storey)
    


    
###################### SLAB generado a partir de column #####################################################
def create_ifcSlab(ifcfile, cx=0,cy=0,cz=0, bx = 0.2, by = 0.2, eSlab = 3.3,slabTag="aSlab"):

    # slab creation: Define the slab shape as a polyline axis and an extruded area solid
    slab_placement = create_ifclocalplacement(ifcfile, relative_to=storey_placement)
    polyline = create_ifcpolyline(ifcfile, [(cx-0.5*bx, cy, cz), (cx+0.5*bx , cy, cz)])
    axis_representation = ifcfile.createIfcShapeRepresentation(context, "Axis", "Curve2D", [polyline])

    extrusion_placement = create_ifcaxis2placement(ifcfile, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    point_list_extrusion_area = [(cx-0.5*bx, cy-by*0.5, cz), (cx+0.5*bx, cy-by*0.5, cz), (cx+bx*0.5, cy+by*0.5, cz), (cx-bx*0.5, cy+by*0.5, cz), (cx-0.5*bx, cy-by*0.5, cz)]
    solid = create_ifcextrudedareasolid(ifcfile, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), eSlab)
    body_representation = ifcfile.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])

    product_shape = ifcfile.createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])
    slab_type = ifcfile.createIfcSlabType('FLOOR')
    slab = ifcfile.createIfcSlab(create_guid(), owner_history, slabTag, "An awesome BIM slab", 'Floor:Concrete Slab', slab_placement, product_shape,None, 'FLOOR')

    # Define and associate the slab material
    material = ifcfile.createIfcMaterial("slab material")
    material_layer = ifcfile.createIfcMaterialLayer(material, eSlab, None)
    material_layer_set = ifcfile.createIfcMaterialLayerSet([material_layer], None)
    material_layer_set_usage = ifcfile.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", -0.1)
    ifcfile.createIfcRelAssociatesMaterial(create_guid(), owner_history, RelatedObjects=[slab], RelatingMaterial=material_layer_set_usage)

    # Create and assign property set
    property_values = [
        ifcfile.createIfcPropertySingleValue("Reference", "Reference", ifcfile.create_entity("IfcText", "Describe the Reference"), None),
        ifcfile.createIfcPropertySingleValue("IsExternal", "IsExternal", ifcfile.create_entity("IfcBoolean", True), None),
        ifcfile.createIfcPropertySingleValue("ThermalTransmittance", "ThermalTransmittance", ifcfile.create_entity("IfcReal", 2.569), None),
        ifcfile.createIfcPropertySingleValue("IntValue", "IntValue", ifcfile.create_entity("IfcInteger", 2), None)]
    property_set = ifcfile.createIfcPropertySet(create_guid(), owner_history, "Pset_SlabCommon", None, property_values)
    ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [slab], property_set)

    # Add quantity information
    quantity_values = [
        ifcfile.createIfcQuantityLength("Length", "Length of the slab", None, (bx+by)*2),
        ifcfile.createIfcQuantityArea("Area", "Area of the front face", None, bx*by),
        ifcfile.createIfcQuantityVolume("Volume", "Volume of the slab", None, bx * by * eSlab)]
    
    element_quantity = ifcfile.createIfcElementQuantity(create_guid(), owner_history, "BaseQuantities", None, None, quantity_values)
    ifcfile.createIfcRelDefinesByProperties(create_guid(), owner_history, None, None, [slab], element_quantity)

    # Relate the window and wall to the building storey
    ifcfile.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, "Building Storey Container", None, [slab], building_storey)

   


                                    
####################################
### PROCEED TO CREATE ELEMENTS


currentLevel=[]
print('Niveles total:',totalLevels)
zFloor=0.0
cz=0.0

for i in range(levelNr):
    print('Nivel:',i)
    currentLevel=levelsData[i]
    #print('Datos de Nivel:',currentLevel)    

    #hCol= float(levelsData[i][0])
    hCol= hColList[i]
    #print('hCol:',hCol)
   # print(levelsData[0][1])                 
    columnsIndex= levelsData[i][1]
    #print('IndexCol:',columnsIndex)
    beamsIndex= levelsData[i][2]
    #print('IndexBeam:',beamsIndex)
    slabsIndex= levelsData[i][3]
    #print('IndexSlab:',slabsIndex)
    
    
    
    
    zFloor=zFloor+hCol
    storey_placement = ifcfile.by_type("IfcBuildingStorey")[i]
    
    for col in columnsIndex:
        
        cTag = col['tag']
        cx = col['cx']
        cy = col['cy']
        bx = col['bx']
        by = col['by']
        cz=zFloor
        
        print('hCol:',hCol)
        print('hCol:',hCol,'zFloor:',zFloor,'cx:',cx,'cy:',cy,'cz:',cz,'bx:',bx,'by:',by,'ctag:',cTag)
        create_ifcColumn(ifcfile,cx,cy,zFloor-hCol,bx,by,hCol,cTag)
        
    #zFloor=0.0
    for slab in slabsIndex:

    #    hCol= float(levelsData[i][0])
    #    zFloor=hCol+zFloor
        sTag = slab['tag']
        cx = slab['cx']
        cy = slab['cy']
        bx = slab['bx']
        by = slab['by']
        eSlab = slab['hSlab']
   #     cz=zFloor
        create_ifcSlab(ifcfile,cx,cy,zFloor,bx,by,eSlab,sTag)
    
    for beam in beamsIndex:

   #     hCol= float(levelsData[i][0])
   #     zFloor=hCol+zFloor
        bTag = beam['tag']
        cxi = beam['data']['cx']
        cyi = beam['data']['cy']
        wBeam = beam['data']['width']
        hBeam = beam['data']['height']
        lBeam = beam['data']['lenght']
        vBeam = beam['data']['direction']
    #    cz=zFloor
        section2 = Rect_Section(b= wBeam, h=hBeam)
        create_ifcBeam(ifcfile ,storey_placement, bTag ,section= section2 ,L=lBeam ,position=(cxi,cyi,zFloor) , direction=vBeam)                                   





ifcfile.write(filename)

print('Done!\n\n')
#print('beamsIndex:',beamsIndex)
#print('slabsIndex:',slabsIndex)    


# In[40]:


print(hColList)


# # Ajustar ancho de pantalla

# In[1]:


from IPython.core.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))

