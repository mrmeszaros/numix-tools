from unittest import TestCase, main
from point import Point
import math


sin = lambda d: round(math.sin(math.radians(d)), 4)
cos = lambda d: round(math.cos(math.radians(d)), 4)


def rotate(point, angle, center=None):
	center = center or Point(0, 0)
	sa = sin(angle)
	ca = cos(angle)
	q = point - center
	x = q.x * ca - q.y * sa
	y = q.x * sa + q.y * ca
	return Point(x, y) + center


# https://math.stackexchange.com/questions/65503/point-reflection-over-a-line#65525
class Mirror:
	@staticmethod
	def v(p, x):
		dx = x - p.x
		return Point(p.x + 2*dx, p.y)

	@staticmethod
	def h(p, y):
		dy = y - p.y
		return Point(p.x, p.y + 2*dy)


class TransformTest(TestCase):
	@classmethod
	def setUpClass(cls):
		global o, p, q
		o = Point(0, 0)
		p = Point(1, 2)
		q = Point(-2, 1)

	def test_rotate(self):
		self.assertEqual(rotate(p, 90), q)
		self.assertEqual(rotate(p, 180), -p)
		self.assertEqual(rotate(p, -90), -q)

	def test_mirror(self):
		self.assertEqual(Mirror.v(p, 0), Point(-1, 2))
		self.assertEqual(Mirror.h(p, 0), Point(1, -2))
		self.assertEqual(Mirror.v(p, 3), Point(5, 2))
		self.assertEqual(Mirror.h(p, 3), Point(1, 4))


if __name__ == '__main__':
	main()
