from abc import ABCMeta, abstractmethod
import ifcopenshell
import uuid
igui=0
class BuildingElement(metaclass=ABCMeta):

    def __init__(self,ifcModelGenerator):
        self.O = (0., 0., 0.)
        self.X = (1., 0., 0.)
        self.Y = (0., 1., 0.)
        self.Z = (0., 0., 1.)
        self.ifcModelGenerator = ifcModelGenerator
  
    def setTripleCartesian(self,O = (0., 0., 0.),X = (1., 0., 0.),Y = (0., 1., 0.), Z = (0., 0., 1.)):
        self.O = O
        self.X = X
        self.Y = Y
        self.Z = Z
        
    def getGUId(self):
    	return self.ifcModelGenerator.getGUId() 

    def getProject(self):
    	return self.ifcModelGenerator.getProject() 
    	
    def getIfcFile(self):
    	return self.ifcModelGenerator.getIfcFile()

    def getOwnerHistory(self):
    	return self.ifcModelGenerator.getOwnerHistory()
    	
    def getContext(self):
    	return self.ifcModelGenerator.getContext() 
  
    def getStoreyPlacement(self):
    	return self.ifcModelGenerator.getStoreyPlacement() 


    	
    def create_ifcpolyline(self, point_list):
        '''Creates an IfcPolyLine from a list of points, specified as Python tuples'''
        ifcpts = []
        for point in point_list:
            point = self.getIfcFile().createIfcCartesianPoint(point)
            ifcpts.append(point)
        polyline = self.getIfcFile().createIfcPolyLine(ifcpts)
        return polyline

    
    def create_ifcextrudedareasolid(self, point_list, ifcaxis2placement, extrude_dir, extrusion):
        '''Creates an IfcExtrudedAreaSolid from a list of points, specified as Python tuples'''
        polyline = self.create_ifcpolyline(point_list)
        ifcclosedprofile = self.getIfcFile().createIfcArbitraryClosedProfileDef("AREA", None, polyline)
        ifcdir = self.getIfcFile().createIfcDirection(extrude_dir)
        ifcextrudedareasolid = self.getIfcFile().createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
        return ifcextrudedareasolid
    
    def create_ifcaxis2placement(self,O,dir1,dir2):
        '''Creates an IfcAxis2Placement3D from Location, Axis and RefDirection specified as Python tuples'''
        point =self.getIfcFile().createIfcCartesianPoint(O)
        dir1 = self.getIfcFile().createIfcDirection(dir1)
        dir2 = self.getIfcFile().createIfcDirection(dir2)
        axis2placement = self.getIfcFile().createIfcAxis2Placement3D(point, dir1, dir2)
        return axis2placement

    def create_ifclocalplacement(self,relative_to=None):
        '''Creates an IfcLocalPlacement from Location, Axis and RefDirection, specified as Python tuples, and relative placement'''
        
        axis2placement = self.create_ifcaxis2placement(self.O,self.Z,self.X)
        ifclocalplacement2 = self.getIfcFile().createIfcLocalPlacement(relative_to,axis2placement)
        return ifclocalplacement2
        
    def buildHierarchy(self):
        '''IFC hierarchy creation'''
       
        site_placement = self.create_ifclocalplacement()
        
        site = self.getIfcFile().createIfcSite(self.getGUId(), self.getOwnerHistory(), "Site", None, None, site_placement, None, None, "ELEMENT", None, None, None, None, None)

        building_placement = self.create_ifclocalplacement(relative_to=site_placement)
        
        building = self.getIfcFile().createIfcBuilding(self.getGUId(), self.getOwnerHistory(), 'Building', None, None, building_placement, None, None, "ELEMENT", None, None, None)
        storey_placement = self.create_ifclocalplacement(relative_to=building_placement)
        building_storey = self.getIfcFile().createIfcBuildingStorey(self.getGUId(), self.getOwnerHistory(), 'StoreyBIM', None, None, storey_placement, None, None, "ELEMENT", self.elevation)
        container_storey = self.getIfcFile().createIfcRelAggregates(self.getGUId(), self.getOwnerHistory(), "Building Container", None, building, [building_storey])
        container_site = self.getIfcFile().createIfcRelAggregates(self.getGUId(), self.getOwnerHistory(), "Site Container", None, site, [building])
        container_project = self.getIfcFile().createIfcRelAggregates(self.getGUId(), self.getOwnerHistory(), "Project Container", None, self.getProject(), [site])
        
        self.ifcModelGenerator.storey_placement=storey_placement

        
    def buildExtrusionShape(self):
        '''Define the building element shape as a polyline axis and an extruded area solid'''
        product_placement = self.create_ifclocalplacement(relative_to=self.getStoreyPlacement())
        self.product_placement=product_placement
        polyline = self.create_ifcpolyline([(self.cx-0.5*self.bx, self.cy, self.cz), (self.cx+0.5*self.bx , self.cy, self.cz)])
        axis_representation = self.getIfcFile().createIfcShapeRepresentation(self.getContext(), "Axis", "Curve2D", [polyline])

        extrusion_placement = self.create_ifcaxis2placement(self.O, self.Z, self.X)
        point_list_extrusion_area = [(self.cx-0.5*self.bx, self.cy-self.by*0.5, self.cz), (self.cx+0.5*self.bx, self.cy-self.by*0.5, self.cz), (self.cx+self.bx*0.5, self.cy+self.by*0.5, self.cz), (self.cx-self.bx*0.5, self.cy+self.by*0.5, self.cz), (self.cx-0.5*self.bx, self.cy-self.by*0.5, self.cz)]
        solid = self.create_ifcextrudedareasolid(point_list_extrusion_area, extrusion_placement, self.Z, self.height)
        body_representation = self.getIfcFile().createIfcShapeRepresentation(self.getContext(), "Body", "SweptSolid", [solid])

        product_shape = self.getIfcFile().createIfcProductDefinitionShape(None, None, [axis_representation, body_representation])
        self.product_shape=product_shape


    def buildRelAssociatesMaterial(self):
        '''Define and associate the building element material'''
        material = self.getIfcFile().createIfcMaterial("the material")
        material_layer = self.getIfcFile().createIfcMaterialLayer(material, 0.2, None)
        material_layer_set = self.getIfcFile().createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = self.getIfcFile().createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", -0.1)
        self.getIfcFile().createIfcRelAssociatesMaterial(self.getGUId(), self.getOwnerHistory(), RelatedObjects=[self.product], RelatingMaterial=material_layer_set_usage)

    def buildPropertySet(self):
        '''Create and assign property set'''
        property_values = [
            self.getIfcFile().createIfcPropertySingleValue("Reference", "Reference", self.getIfcFile().create_entity("IfcText", "Describe the Reference"), None),
            self.getIfcFile().createIfcPropertySingleValue("IsExternal", "IsExternal", self.getIfcFile().create_entity("IfcBoolean", True), None),
            self.getIfcFile().createIfcPropertySingleValue("ThermalTransmittance", "ThermalTransmittance", self.getIfcFile().create_entity("IfcReal", 2.569), None),
            self.getIfcFile().createIfcPropertySingleValue("IntValue", "IntValue", self.getIfcFile().create_entity("IfcInteger", 2), None)
        ]
        property_set = self.getIfcFile().createIfcPropertySet(self.getGUId(), self.getOwnerHistory(), "Pset_ColumnCommon", None, property_values)
        self.getIfcFile().createIfcRelDefinesByProperties(self.getGUId(),self.getOwnerHistory(), None, None, [self.product], property_set)

    def buildElementQuantity(self):
        '''Add quantity information'''
        quantity_values = [
            self.getIfcFile().createIfcQuantityLength("Length", "Length of the column", None, self.height),
            self.getIfcFile().createIfcQuantityArea("Area", "Area of the cross section", None, self.bx * self.by),
            self.getIfcFile().createIfcQuantityVolume("Volume", "Volume of the column", None, self.height * self.bx * self.by)
        ]
        element_quantity = self.getIfcFile().createIfcElementQuantity(self.getGUId(), self.getOwnerHistory(), "BaseQuantities", None, None, quantity_values)
        self.getIfcFile().createIfcRelDefinesByProperties(self.getGUId(), self.getOwnerHistory(), None, None, [self.product], element_quantity)

    def buildRelateToBuildingStorey(self):
        self.getIfcFile().createIfcRelContainedInSpatialStructure(self.getGUId(), self.getOwnerHistory(), "Building Storey Container", None, [self.product], self.getBuildingStorey())     
   

