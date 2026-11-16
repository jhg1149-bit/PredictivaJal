import unittest
from core.risk import Reading, calculate_risk
class RiskTests(unittest.TestCase):
 def test_normal(self):
  r=calculate_risk(Reading("A","inyectora",65,1.5,12,100)); self.assertEqual(r["irf"],0); self.assertEqual(r["level"],"Normal")
 def test_critical(self):
  r=calculate_risk(Reading("A","inyectora",95,4.5,25,500)); self.assertEqual(r["irf"],100); self.assertEqual(r["level"],"Crítico")
 def test_warning_range(self):
  r=calculate_risk(Reading("A","cnc",80,3,18.5,300)); self.assertGreaterEqual(r["irf"],40); self.assertLess(r["irf"],70)
 def test_negative_rejected(self):
  with self.assertRaises(ValueError): calculate_risk(Reading("A","cnc",-1,1,1,1))
 def test_invalid_profile(self):
  with self.assertRaises(ValueError): calculate_risk(Reading("A","robot",1,1,1,1))
if __name__=="__main__": unittest.main()
