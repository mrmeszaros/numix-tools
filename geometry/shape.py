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
		return NotImplemented


class Line(Shape):
	def __init__(self, p0, p1):
		self._data = (p0, p1)

	def __iter__(self):
		return iter(self._data)

	def __intersect__(self, other):
		if isinstance(other, Circle):
			return self.__intersect_circle(other)
		return NotImplemented

	def __intersect_circle(self, circle):
		p1, p2 = self
		c, r = circle
		p1 = p1 - c
		p2 = p2 - c
		dx = p2.x - p1.x
		dy = p2.y - p1.y
		dr2 = dx*dx + dy*dy
		D = p1.x*p2.y - p2.x*p1.y
		discriminant = r*r*dr2 - D*D
		if discriminant < 0:
			return tuple()
		if discriminant == 0:
			return (Point(1.0*D*dy/dr2, -1.0*D*dx/dr2) + c,)
		sd = sqrt(discriminant)
		xdiff = copysign(dx*sd, dy*dx)
		ydiff = abs(dy)*sd
		return (Point(D*dy - xdiff, -D*dx - ydiff) / dr2 + c, Point(D*dy + xdiff, -D*dx + ydiff) / dr2 + c)
