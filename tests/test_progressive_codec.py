import ctypes
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'validation/cooja'

class CodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        path=Path(cls.tmp.name)/'codec.so'
        subprocess.run(['gcc','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC',str(SOURCE/'codec.c'),'-o',str(path)],check=True)
        cls.lib=ctypes.CDLL(str(path))
        cls.lib.study_encode.argtypes=[ctypes.POINTER(ctypes.c_int16),ctypes.c_uint,ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.study_encode.restype=ctypes.c_size_t
        cls.lib.study_decode.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.c_uint,ctypes.POINTER(ctypes.c_int16)]
        cls.lib.study_decode.restype=ctypes.c_int
        cls.lib.study_quantization_sse.argtypes=[ctypes.POINTER(ctypes.c_int16),ctypes.c_uint]
        cls.lib.study_quantization_sse.restype=ctypes.c_uint64
        cls.lib.study_rd_choose.argtypes=[ctypes.POINTER(ctypes.c_int16),ctypes.c_double]
        cls.lib.study_rd_choose.restype=ctypes.c_uint
        cls.lib.study_rd_update.argtypes=[ctypes.c_double,ctypes.c_uint]
        cls.lib.study_rd_update.restype=ctypes.c_double
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def encode(self,values,bits):
        a=(ctypes.c_int16*250)(*values);data=(ctypes.c_uint8*500)();out=(ctypes.c_int16*250)()
        n=self.lib.study_encode(a,bits,data)
        ok=self.lib.study_decode(data,n,bits,out)
        self.assertEqual(ok,1)
        return n,list(out)
    def test_lossless_full_report_and_signed_extremes(self):
        rng=random.Random(42)
        values=[-32768,-1,0,1,32767]+[rng.randint(-32768,32767) for _ in range(245)]
        n,out=self.encode(values,16)
        self.assertEqual(n,500);self.assertEqual(out,values)
    def test_progressive_payload_sizes_and_error_bound(self):
        values=[-32768+int(i*65535/249) for i in range(250)]
        for bits,expected in [(4,125),(8,250),(12,375)]:
            n,out=self.encode(values,bits)
            self.assertEqual(n,expected)
            self.assertLessEqual(max(abs(x-y) for x,y in zip(values,out)),2**(15-bits))
    def test_decoder_rejects_truncated_payload(self):
        data=(ctypes.c_uint8*500)();out=(ctypes.c_int16*250)()
        self.assertEqual(self.lib.study_decode(data,124,4,out),0)
    def test_invalid_depth_is_rejected(self):
        values=(ctypes.c_int16*250)();data=(ctypes.c_uint8*500)()
        for bits in [0,17]:self.assertEqual(self.lib.study_encode(values,bits,data),0)
    def test_local_distortion_equals_actual_decoded_error(self):
        rng=random.Random(91);values=[rng.randint(-32768,32767) for _ in range(250)]
        a=(ctypes.c_int16*250)(*values)
        for bits in [4,8,12,16]:
            _,out=self.encode(values,bits)
            self.assertEqual(self.lib.study_quantization_sse(a,bits),sum((x-y)**2 for x,y in zip(values,out)))
    def test_rd_price_changes_decision_and_dual_update_direction(self):
        a=(ctypes.c_int16*250)(*[100]*250)
        self.assertEqual(self.lib.study_rd_choose(a,0),16)
        self.assertEqual(self.lib.study_rd_choose(a,1000),4)
        self.assertGreater(self.lib.study_rd_update(.1,16),.1)
        self.assertLess(self.lib.study_rd_update(.1,4),.1)
        self.assertEqual(self.lib.study_rd_update(0,4),0)
