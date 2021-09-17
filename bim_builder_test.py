#python -m unittest bim_builder_test.py
import faulthandler; faulthandler.enable()
from IfcModelGenerator import *
import unittest
    
parser = Parser('predicciones_full','relacionados_full')
parser.build()
model = IfcModelGenerator(parser)
model.builder()

class TestBimBuilder_Integral(unittest.TestCase):
    def test_column(self):
        self.assertAlmostEqual(len(model.getIfcColumns()),4)
    def test_beams(self):
        self.assertAlmostEqual(len(model.getIfcBeams()),4)
    def test_slabs(self):
        self.assertAlmostEqual(len(model.getIfcSlabs()),1)
