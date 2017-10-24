import numpy as np

class Line:
	def __init__(self,line_array=[0,0,0,0]):
		self.x1 = line_array[0]
		self.y1 = line_array[1]
		self.x2 = line_array[2]
		self.y2 = line_array[3]

	def slope(self): return (self.y2-self.y1) / (self.x2-self.x1+0.0001)
	def intercept(self): 	return self.y1 - self.slope()*self.x1
	def length(self): 		return np.sqrt((self.y2-self.y1)**2+(self.x2-self.x1)**2)

	def greater_x(self):	return self.x1 if self.x1 > self.x2 else self.x2
	def greater_y(self):	return self.y1 if self.y1 > self.y2 else self.y2
	def smaller_x(self):	return self.x1 if self.x1 < self.x2 else self.x2
	def smaller_y(self):	return self.y1 if self.y1 < self.y2 else self.y2

	def inclination(self):  return np.rad2deg(np.arctan(self.slope()))

	def point_1(self): return (self.x1, self.y1)	
	def point_2(self): return (self.x2, self.y2)

	def __repr__(self): return str([self.x1,self.y1,self.x2,self.y2])

