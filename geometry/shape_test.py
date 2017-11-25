from unittest import TestCase, main
from point import Point as P
from shape import Shape, Line as L, Circle as C, intersect


class ShapeTest(TestCase):
	def test_shape_is_abstract(self):
		self.assertRaises(TypeError, Shape)

	def test_line_line_intersecttion(self):
		l1 = L(P(1, 0), P(0, 1))
		l2 = L(P(0, 0), P(1, 1))
		self.assertEqual(P(.5, .5), intersect(l1, l2))
		l3 = L(P(2, 0), P(0, 2))
		self.assertEqual(None, intersect(l1, l3))

	def test_line_cirlce_intersection(self):
		o = P(-1, 2)
		c = C(o, 5)
		p1 = P(3, 4) + o
		p2 = -P(3, 4) + o
		# line definition
		self.assertEqual({p1, p2}, set(intersect(L(o, p1), c)))
		self.assertEqual({p1, p2}, set(intersect(L(p1, o), c)))
		# symmetric
		self.assertEqual(set(intersect(L(o, p1), c)), set(intersect(c, L(p1, o))))


if __name__ == '__main__':
	main()
