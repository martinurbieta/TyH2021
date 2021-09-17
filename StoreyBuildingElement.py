import ifcopenshell
from BuildingElement import *

class Storey(BuildingElement):
    def __init__(self,ifcModelGenerator, elevation=0):
        self.elevation = elevation
        self.ifcModelGenerator = ifcModelGenerator
        self.O = 0., 0., 0.
        self.X = 1., 0., 0.
        self.Y = 0., 1., 0.
        self.Z = 0., 0., 1.
        
    def getElevation(self):
        elevation=self.elevation
        return elevation  
 	


