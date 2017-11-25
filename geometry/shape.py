from abc import ABC, abstractmethod
from point import Point
from math import sqrt, copysign


def intersect(s1, s2):
	# TODO create underlying methods for the API to work
	result = s1.__intersect__(s2)
	if result == NotImplemented:
		return s2.__intersect__(s1)
	return result


class Shape(ABC):
	@abstractmethod
	def __intersect__(self, other):
		pass


class Circle(Shape):
	"""docstring for Circle"""
	def __init__(self, origin, radius):
		self.o = origin
		self.r = radius

	def __iter__(self):
		return iter((self.o, self.r))

	def __intersect__(self, other):
		if isinstance(other, Circle):
			return self.__intersect_circle(other)
		return NotImplemented

	def __intersect_circle(self, circle):
		p0, r0 = self
		p1, r1 = circle
		q = p1 - p0
		d = abs(q)
		if d > r0 + r1 or d < abs(r0 - r1) or d == 0:
			return tuple()
		a = (r0**2 - r1**2 + d**2) / (2*d)
		h = sqrt(r0**2 - a**2)
		p2 = p0 + a*q / d
		qq = Point(-q.y, q.x)
		if h == 0:
			return (p2,)
		return (p2 + h*qq/d, p2 - h*qq/d)


class Line(Shape):
	def __init__(self, p0, p1):
		self._data = (p0, p1)

	def __iter__(self):
		return iter(self._data)

	def __intersect__(self, other):
		if isinstance(other, Line):
			return self.__intersect_line(other)
		if isinstance(other, Circle):
			return self.__intersect_circle(other)
		return NotImplemented

	def __intersect_circle(self, circle):
		p0, p1 = self
		c, r = circle
		p0 = p0 - c
		p1 = p1 - c
		dx = p1.x - p0.x
		dy = p1.y - p0.y
		dr2 = dx*dx + dy*dy
		D = p0.x*p1.y - p1.x*p0.y
		discriminant = r*r*dr2 - D*D
		if discriminant < 0:
			return tuple()
		if discriminant == 0:
			return (Point(1.0*D*dy/dr2, -1.0*D*dx/dr2) + c,)
		sd = sqrt(discriminant)
		xdiff = copysign(dx*sd, dy*dx)
		ydiff = abs(dy)*sd
		return (Point(D*dy - xdiff, -D*dx - ydiff) / dr2 + c, Point(D*dy + xdiff, -D*dx + ydiff) / dr2 + c)

	def __intersect_line(self, line):
		a1, b1, c1 = self.__params()
		a2, b2, c2 = line.__params()
		det = a1*b2 - a2*b1
		if abs(det) == 0:
			return None
		return Point(b2*c1 - b1*c2, a1*c2 - a2*c1) / det

	def __params(self):
		p0, p1 = self
		x1, y1 = p0
		x2, y2 = p1
		a = y2 - y1
		b = x1 - x2
		c = a*x1 + b*y1
		return a, b, c
