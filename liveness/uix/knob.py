"""
	Knob
	====
"""
import	math

from	kivy.lang			import	Builder
from	kivy.uix.widget		import	Widget
from	kivy.properties		import	BoundedNumericProperty,NumericProperty,StringProperty

Builder.load_string('''
#KVOperations
<Knob>:
	size_hint:None,None

	canvas.before:
		Color:
			rgba:	1,1,1,1
		PushMatrix
		Rotate:
			angle:	360. - self.angle
			origin:	self.center
		Rectangle:
			pos:	self.pos[0],self.pos[1]
			size:	self.size[0],self.size[1]
			source:	self.source

	canvas:
		PopMatrix

''')

class Knob(Widget):

	angle			=	NumericProperty(0)
	source   		=	StringProperty("")

	def evaluate_angle(self, touch):
		y	=	touch.y-self.center[1]
		x	=	touch.x-self.center[0]
		if y == 0:
			a	=	0
		else:
			a	=	math.atan2(x, y)
		while a < 0.0:
			a	=	a + (math.pi*2)
		return math.degrees(a)

	def	on_touch_down(self, touch):
		if self.collide_point(touch.x, touch.y):
			self.angle	=	self.evaluate_angle(touch)
			self.on_press(touch)

	def	on_touch_move(self, touch):
		if self.collide_point(touch.x, touch.y):
			self.angle	=	self.evaluate_angle(touch)
			self.on_press(touch)

	def	on_press(self, touch):
		pass
