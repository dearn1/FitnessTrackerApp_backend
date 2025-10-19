from django.test import SimpleTestCase

class SimpleTest(SimpleTestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)
