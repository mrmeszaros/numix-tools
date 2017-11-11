#!/usr/bin/env python3

from point import Point as P
from math import sqrt, copysign, hypot


def centers_from_points_and_radius(p1, p2, r):
	d = p2 - p1
	q = sqrt(d.x**2 + d.y**2)
	p3 = (p1 + p2) / 2
	dd = P(-d.y, d.x)
	s = sqrt(r**2 - (q/2)**2)
	t = s/q*dd
	return (p3 + t, p3 - t)


def intersect(p1, p2, c, r):
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
		return (P(1.0*D*dy/dr2, -1.0*D*dx/dr2) + c,)
	sd = sqrt(discriminant)
	xdiff = copysign(dx*sd, dy)
	ydiff = abs(dy)*sd
	return (P(D*dy - xdiff, -D*dx - ydiff) / dr2 + c, P(D*dy + xdiff, -D*dx + ydiff) / dr2 + c)


def intersect_circles(p0, r0, p1, r1):
	q = p1 - p0
	d = abs(q)
	if d > r0 + r1 or d < abs(r0 - r1) or d == 0:
		return tuple()
	a = (r0**2 - r1**2 + d**2) / (2*d)
	h = sqrt(r0**2 - a**2)
	p2 = p0 + a*q / d
	qq = P(-q.y, q.x)
	return (p2 + h*qq/d, p2 - h*qq/d)
