from pathlib import Path
import sys,tempfile,unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'validation/cooja'))
from analyse import analyse,exact_signflip,holm
class AnalysisTests(unittest.TestCase):
    def test_empty_outputs_are_not_research_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):analyse(d)
    def test_exact_resolution_for_ten_pairs(self):
        self.assertAlmostEqual(exact_signflip(np.arange(1,11)),2/1024)
    def test_holm_is_monotone_in_rank(self):
        np.testing.assert_allclose(holm([.03,.001,.02]),[.04,.003,.04])
