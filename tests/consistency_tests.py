""" Test cases used to test for consistency"""
import unittest

from organ_templates.organ import Organ
from model import Model, os


class TestConsistency(unittest.TestCase):
    m = None

    @classmethod
    def setUpClass(cls):
        cls.m = Model(os.path.abspath('..'))

    def test_trivial_consistency(self):
        self.assertEqual(self.m.check_global_consistency(), True)

    def test_global_consistency(self):
        self.m.add_organ(Organ("heart", "SystemicParameters"), 0.04, *self.m.get_systemic())
        self.assertEqual(self.m.check_global_consistency(), True)

    @classmethod
    def tearDownClass(cls):
        cls.m.close()