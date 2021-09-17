from BuildingElement import *
import sys
FREECADPATH = '/usr/lib/freecad-python3/lib'
sys.path.append(FREECADPATH)
from FreeCAD import Vector

class Beam(BuildingElement):
    def __init__(self, ifcModelGenerator,building_storey,tag="",AreaProfile="", lenght=0, position=(0,0,0),direction=(0,0,0)):
        self.O = 0., 0., 0.
        self.X = 1., 0., 0.
        self.Y = 0., 1., 0.
        self.Z = 0., 0., 1.
        self.ifcModelGenerator = ifcModelGenerator
        self.tag=tag
        self.building_storey=building_storey
        self.product=""
        self.direction = direction
        self.position = position
        self.lenght=lenght
        self.AreaProfile = AreaProfile
        
    def getBuildingStorey(self):
        return self.building_storey 
    
    def getAreaProfile(self):
        return self.AreaProfile
    
    def getProduct(self):
        return self.product

    def getDirection(self):
        return self.direction 
        
    def buildExtrusionShape(self):
        Point =self.getIfcFile().createIfcCartesianPoint ( self.position ) 
        Axis2Placement = self.getIfcFile().createIfcAxis2Placement3D(Point)
        Axis2Placement.Axis = self.getIfcFile().createIfcDirection(self.getDirection())
        Axis2Placement.RefDirection =self.getIfcFile().createIfcDirection(Vector(self.getDirection()).cross(Vector(self.Z)))
        
        Placement = self.getIfcFile().createIfcLocalPlacement(self.getBuildingStorey().ObjectPlacement,Axis2Placement)
        self.getProduct().ObjectPlacement=Placement
    
        product_ExtrudePlacement = self.getIfcFile().createIfcAxis2Placement3D(self.getIfcFile().createIfcCartesianPoint ( self.O )   )
	   
        product_Extruded=self.getIfcFile().createIfcExtrudedAreaSolid()
        product_Extruded.SweptArea=self.getAreaProfile()
        product_Extruded.Position=product_ExtrudePlacement
        product_Extruded.ExtrudedDirection = self.getIfcFile().createIfcDirection(self.Z)
        product_Extruded.Depth = self.lenght
	    
        product_Repr=self.getIfcFile().createIfcShapeRepresentation()
        product_Repr.ContextOfItems=self.getContext()
        product_Repr.RepresentationIdentifier = 'Body'
        product_Repr.RepresentationType = 'SweptSolid'
        product_Repr.Items = [product_Extruded]
	    
        product_DefShape=self.getIfcFile().createIfcProductDefinitionShape()
        product_DefShape.Representations=[product_Repr]
        self.getProduct().Representation=product_DefShape
	    
        Floor_Container = self.getIfcFile().createIfcRelContainedInSpatialStructure(self.getGUId(),self.getOwnerHistory() )
        Floor_Container.RelatedElements=[self.getProduct()]
        Floor_Container.RelatingStructure= self.getBuildingStorey()
        
    def buildProduct(self):        
        beam = self.getIfcFile().createIfcBeam(self.getGUId(),self.getOwnerHistory() , self.tag)
        self.product=beam
        self.getProduct().ObjectType ='beam'
        
    def buildRelAssociatesMaterial(self):
        '''Define and associate the building element material'''    
        material = self.getIfcFile().createIfcMaterial("beam material")
        material_layer = self.getIfcFile().createIfcMaterialLayer(material, self.lenght/200, None)
        material_layer_set = self.getIfcFile().createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = self.getIfcFile().createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", -0.1)
        self.getIfcFile().createIfcRelAssociatesMaterial(self.getGUId(), self.getOwnerHistory(), RelatedObjects=[self.getProduct()], RelatingMaterial=material_layer_set_usage)
        
    def buildPropertySet(self):
        property_values = [
        self.getIfcFile().createIfcPropertySingleValue("Reference", "Reference", self.getIfcFile().create_entity("IfcText", "Describe the Reference"), None),
        self.getIfcFile().createIfcPropertySingleValue("IsExternal", "IsExternal", self.getIfcFile().create_entity("IfcBoolean", True), None),
        self.getIfcFile().createIfcPropertySingleValue("ThermalTransmittance", "ThermalTransmittance", self.getIfcFile().create_entity("IfcReal", 2.569), None),
        self.getIfcFile().createIfcPropertySingleValue("IntValue", "IntValue", self.getIfcFile().create_entity("IfcInteger", 2), None)
    ]
        property_set = self.getIfcFile().createIfcPropertySet(self.getGUId(), self.getOwnerHistory(), "Pset_BeamCommon", None, property_values)
        self.getIfcFile().createIfcRelDefinesByProperties(self.getGUId(), self.getOwnerHistory(), None, None, [self.product], property_set)
 
    def buildElementQuantity(self):
        '''Add quantity information'''    
        quantity_values = [
        	self.getIfcFile().createIfcQuantityLength("Length", "Length of the beam", None, self.lenght),
 		self.getIfcFile().createIfcQuantityArea("Area", "Area of the cross section", None, self.getAreaProfile().XDim * self.getAreaProfile().YDim),
  		self.getIfcFile().createIfcQuantityVolume("Volume", "Volume of the column", None, self.getAreaProfile().XDim * self.getAreaProfile().YDim * self.lenght)
    ]
        element_quantity = self.getIfcFile().createIfcElementQuantity(self.getGUId(), self.getOwnerHistory(), "BaseQuantities", None, None, quantity_values)
        self.getIfcFile().createIfcRelDefinesByProperties(self.getGUId(), self.getOwnerHistory(), None, None, [self.product], element_quantity)        

    def I_Section(self,W ,D , tw , tf  , r):
        beam_Axis2Placement2D =self.getIfcFile().createIfcAxis2Placement2D(self.getIfcFile().createIfcCartesianPoint( (0.,0.) ) )
    
        self.AreaProfile = self.getIfcFile().createIfcIShapeProfileDef('AREA')
        self.getAreaProfile().Position = beam_Axis2Placement2D 
        self.getAreaProfile().OverallWidth = W
        self.getAreaProfile().OverallDepth = D
        self.getAreaProfile().WebThickness = tw
        self.getAreaProfile().FlangeThickness = tf
        self.getAreaProfile().FilletRadius=r
        return self.AreaProfile

    def L_Section(self,W ,D , t   , r):
        beam_Axis2Placement2D =self.getIfcFile().createIfcAxis2Placement2D(self.getIfcFile().createIfcCartesianPoint( (0.,0.) ) )
    
        self.AreaProfile = self.getIfcFile().createIfcLShapeProfileDef('AREA')
        self.getAreaProfile().Position = beam_Axis2Placement2D 
        self.getAreaProfile().Width = W
        self.getAreaProfile().Depth = D
        self.getAreaProfile().Thickness = t

        self.getAreaProfile().FilletRadius=r
        return self.AreaProfile

    def U_Section(self,W ,D , tw  , tf  , r):
        beam_Axis2Placement2D =self.getIfcFile().createIfcAxis2Placement2D( self.getIfcFile().createIfcCartesianPoint( (0.,0.) ) )
        self.AreaProfile = self.getIfcFile().createIfcUShapeProfileDef('AREA')
        self.getAreaProfile().Position = beam_Axis2Placement2D 
        self.getAreaProfile().FlangeWidth = W
        self.getAreaProfile().Depth = D
        self.getAreaProfile().WebThickness = tw
        self.getAreaProfile().FlangeThickness = tf
        self.getAreaProfile().FilletRadius=r
        self.getAreaProfile().EdgeRadius=r*0.5
        return self.AreaProfile

    def Rect_Section(self,b, h):
        beam_Axis2Placement2D =self.getIfcFile().createIfcAxis2Placement2D(self.getIfcFile().createIfcCartesianPoint( (0.,0.) ) )
        self.AreaProfile = self.getIfcFile().createIfcRectangleProfileDef('AREA')
        self.getAreaProfile().Position = beam_Axis2Placement2D 
        self.getAreaProfile().XDim = b
        self.getAreaProfile().YDim = h
        return self.AreaProfile

    def builder(self):
        self.buildProduct()
        self.buildExtrusionShape()
        self.buildRelAssociatesMaterial()
        self.buildPropertySet()
        self.buildElementQuantity()
        self.buildRelateToBuildingStorey()
            
