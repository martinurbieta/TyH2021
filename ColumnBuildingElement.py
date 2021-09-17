from BuildingElement import *

class Column(BuildingElement):
    def __init__(self, ifcModelGenerator,building_storey, cx=0.0,cy=0.0,cz=0.0, column_bx = 0.2, column_by = 0.2, column_h = 3.3,ctag=""):
        self.O = 0., 0., 0.
        self.X = 1., 0., 0.
        self.Y = 0., 1., 0.
        self.Z = 0., 0., 1.
        self.ifcModelGenerator = ifcModelGenerator
        self.cx=cx
        self.cy=cy
        self.cz=cz
        self.bx=column_bx
        self.by=column_by
        self.tag=ctag
        self.height=column_h
        self.building_storey=building_storey
        self.product=""
        self.product_shape=""
        self.product_placement=""

    def getProductShape(self):
        return self.product_shape 
    
    def getProduct(self):
        return self.product 
    
    def getProductPlacement(self):
        return self.product_placement
        
    def getBuildingStorey(self):
        return self.building_storey 

    def buildProduct(self):
        print()
        column = self.getIfcFile().createIfcColumn(self.getGUId(), self.getOwnerHistory(), "Columna", "Una columna increible", None, self.getProductPlacement(),self.getProductShape(), None)
        self.product=column     
        
    def builder(self):
    	
    	self.buildExtrusionShape()
    	self.buildProduct()
    	self.buildRelAssociatesMaterial()
    	self.buildPropertySet()
    	self.buildElementQuantity()
    	self.buildRelateToBuildingStorey()
    	    
