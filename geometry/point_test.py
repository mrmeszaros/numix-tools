from unittest import TestCase, main
from point import Point


class PointTest(TestCase):
	@classmethod
	def setUpClass(cls):
		global o, p, q
		o = Point(0, 0)
		p = Point(1, 2)
		q = Point(2, 3)

	def test_equality(self):
		self.assertTrue(p == Point(1, 2))
		self.assertTrue(p == Point(1.0, 2.0))
		self.assertTrue(p != q)

	def test_default_values(self):
		self.assertEqual(o, Point())

	def test_coordinate_access(self):
		p_x, p_y = p
		self.assertEqual(p_x, 1)
		self.assertEqual(p_y, 2)
		self.assertEqual(q.x, 2)
		self.assertEqual(q.y, 3)

	def test_addition(self):
		self.assertEqual(p + q, Point(3, 5))

	def test_subtraction(self):
		self.assertEqual(p - q, Point(-1, -1))

	def test_negation(self):
		self.assertEqual(-p, Point(-1, -2))
		self.assertEqual(-o, o)

	def test_scaling(self):
		# Can multiply by scalar
		self.assertEqual(2 * p, Point(2, 4))
		self.assertEqual(p * 3, Point(3, 6))
		# Can divide by scalar
		self.assertEqual(Point(2, 4) / 2, p)
		self.assertEqual(o / 3, o)

	def test_length(self):
		self.assertEqual(abs(o), 0)
		self.assertEqual(abs(Point(3, 4)), 5)

	def test_hash(self):
		self.assertEqual(hash(o), hash(Point(0, 0)))


if __name__ == '__main__':
	main()
