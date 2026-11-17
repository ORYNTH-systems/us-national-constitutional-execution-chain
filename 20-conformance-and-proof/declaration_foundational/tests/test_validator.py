import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validator import Claim, AuthorityError, validate

class ClassificationTests(unittest.TestCase):
    def test_declaration_cannot_grant_binding_authority(self):
        with self.assertRaises(AuthorityError):
            validate(Claim('FND-003','FOUNDATIONAL','DOI-1776','P2',True))
    def test_unverified_legal_authority_fails(self):
        with self.assertRaises(AuthorityError):
            validate(Claim('FND-004','BINDING','CONST-ART-I','S1',True,'CONST-ART-I',False))
    def test_missing_provenance_fails(self):
        with self.assertRaises(AuthorityError):
            validate(Claim('FND-001','FOUNDATIONAL','','',False))
    def test_foundational_observation_allowed(self):
        self.assertEqual(validate(Claim('FND-001','FOUNDATIONAL','DOI-1776','P2',False)), 'CLASSIFICATION_PASS')
    def test_verified_legal_classification_allowed(self):
        self.assertEqual(validate(Claim('FND-004','BINDING','CONST-ART-I','S1',True,'CONST-ART-I',True)), 'CLASSIFICATION_PASS')
if __name__ == '__main__': unittest.main()
