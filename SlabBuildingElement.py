from BuildingElement import *

class Slab(BuildingElement):
    def __init__(self, ifcModelGenerator,building_storey, cx=0.0,cy=0.0,cz=0.0, bx = 0.2, by = 0.2, height = 0.2,sTag=""):
        self.O = 0., 0., 0.
        self.X = 1., 0., 0.
        self.Y = 0., 1., 0.
        self.Z = 0., 0., 1.
        self.ifcModelGenerator = ifcModelGenerator
        self.cx=cx
        self.cy=cy
        self.cz=cz
        self.bx=bx
        self.by=by
        self.tag=sTag			
        self.height=height		
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
        slab_type = self.getIfcFile().createIfcSlabType('FLOOR')
        slab = self.getIfcFile().createIfcSlab(self.getGUId(), self.getOwnerHistory(), self.tag, "An awesome BIM slab", 'Floor:Concrete Slab', self.getProductPlacement(), self.getProductShape(),None, 'FLOOR')
        self.product=slab

       
        
    def builder(self):
    	
    	self.buildExtrusionShape()
    	self.buildProduct()
    	self.buildRelAssociatesMaterial()
    	self.buildPropertySet()
    	self.buildElementQuantity()
    	self.buildRelateToBuildingStorey()
    	    
