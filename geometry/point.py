import math


class Point(tuple):
	def __new__(cls, x=0, y=0):
		return super(Point, cls).__new__(cls, (x, y))

	@property
	def x(self):
		return self[0]

	@property
	def y(self):
		return self[1]

	def __abs__(self):
		return math.hypot(self.x, self.y)

	def __add__(self, other):
		x, y = other
		return Point(self.x + x, self.y + y)

	def __sub__(self, other):
		x, y = other
		return Point(self.x - x, self.y - y)

	def __neg__(self):
		return Point(-self.x, -self.y)

	def __mul__(self, scalar):
		return Point(self.x * scalar, self.y * scalar)

	def __rmul__(self, scalar):
		return self * scalar

	def __truediv__(self, scalar):
		return Point(self.x / scalar, self.y / scalar)
