import time
import unittest
from memcache import MemCache

class TestSum(unittest.TestCase):
    def test_SELECTOR(self):
        m1 = MemCache()
        m2 = MemCache(1)
        with self.assertRaises(ValueError):
            m1(16)
        with self.assertRaises(ValueError):
            m2(2)
        raised = False
        try:
            m1(15)
        except:
            raised = True
        self.assertFalse(raised, 'Exception raised')
        del m1
        del m2

    def test_SET(self):
        m = MemCache()
        with self.assertRaises(TypeError):
            m(0).SET(123, 123)
        del m

    def test_GET(self):
        m = MemCache()
        cached_key = "test1"
        cached_value = 222
        m(0).SET(cached_key, cached_value)
        stored_value = m(0).GET(cached_key).value
        self.assertEqual(cached_value, stored_value, "Should be 6")
        del m

    def test_DEL(self):
        m = MemCache()
        with self.assertRaises(TypeError):
            m(0).DEL(123)
        m(0).SET("DEL", 123)
        m(0).DEL("DEL")
        self.assertFalse(m(0).GET("DEL").value, "Item not deleted")
        del m

    def test_MOD(self):
        m = MemCache()
        with self.assertRaises(TypeError):
            m(0).MOD(123, 123)
        m(0).SET('KEY', 1)
        m(0).MOD('KEY', '1')
        self.assertEqual(m(0).GET('KEY').value, '1')
        del m

    def test_LEN(self):
        m = MemCache()
        m(0).SET('KEY1', 1)
        m(0).SET('KEY2', 2)
        self.assertEqual(m(0).LEN().value, 2)
        del m

    def test_EXP(self):
        m = MemCache()
        with self.assertRaises(TypeError):
            m(0).SET("EXP1", 123, "test")
        with self.assertRaises(TypeError):
            m(0).SETEXP("EXP1", "test")
        m(0).SET("EXP2", 123, 1)
        time.sleep(2)
        self.assertFalse(m(0).GET("EXP2").value)
        m(0).SET("EXP3", 123)
        time.sleep(1)
        self.assertEqual(m(0).GETEXP("EXP3").value, -1)
        m(0).SET("EXP4", 123)
        m(0).SETEXP("EXP4", 1)
        time.sleep(2)
        self.assertFalse(m(0).GET("EXP4").value)
        del m

    def test_KEYS(self):
        m = MemCache()
        m(0).SET("KEY1", 1)
        m(0).SET("SET_KEY2", 2)

        self.assertEqual(m(0).KEYS().value, ['KEY1', 'SET_KEY2'])
        self.assertEqual(m(0).KEYS("S").value, ['SET_KEY2'])
        del m

    def test_POP(self):
        m = MemCache()
        m(0).SET("KEY", 1)
        self.assertEqual(m(0).POP("KEY1").value, 1)
        self.assertEqual(m(0).GET("KEY").value, None)
        del m


if __name__ == '__main__':
    unittest.main()