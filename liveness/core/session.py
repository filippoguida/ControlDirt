'''
Session
=======
.. versionadded:: 1.1.0

.. warning::
	This module is highly experimental, use it with care.

:class:`Session` class contain all the rules and the operations needed to
enstablish communication between devices, using open sound control protocol.

OSC Communication
-----------------
Open Sound Control (OSC) is an open, transport-independent, message-based
protocol developed for communication between devices over network.

Born as an alternative to the 1983 MIDI-standard, in comparastion OSC
have many advantages such:

	* the ability to manage infinite number of messages, driven by string patterns
	* using of hierarchical namespaces to manage messages
	* data driven control's resolution, so much accurate respect the 255 values offer by MIDI

For this reasons OSC comed used from many distributed applications also to
manage the communication between its own processes. This is exactly what this
class provide.

Usage
-----
Every session is defined into a ControlSurface's instance context. That means
control surface can communicate beween just one single session::

	cs = ControlSurface()
	cs.session  #this operation will return a Session's instance

This class represent a sort of sub-network reference, where every compoment in
associate can communicate only with others component from the same session::

	For example, in this situation all devices are able to communicate to
	each other, except device 1 and 3 that have not sessions in common
	.. graphviz::
	digraph {
		A -- {"device 1", "device 2", "device 4", "device 5"};
		B -- {"device 2", "device 3"};
		C -- {"device 3", "device 4", "device 5"};
		"Session" -- {A, B, C};
	}

.. warning::
 The Session class is not able to share resources over network, at the moment.
 For this reason is not garantee the working between surfaces in different
 devices sharing the same session.
'''
from 	threading 				import 	 Condition
from	kivy.clock				import   Clock
from	kivy.lib.osc			import   oscAPI

class Session:
	#OSC server intialization - Broadcast listener on port 57121
	oscAPI.init()
	osc_listener 		=   oscAPI.listen('0.0.0.0', 57121)

	#Session instances collector
	instances			=   {}

	#Threading Syncronization Events
	resources_lock		=   Condition()

	#Session Constructor and Creation Conditions
	def __init__(self, session_id):
		#set-up session
		if Session.check(session_id):
			#session already defined
			self = Session.instances[session_id]
		else:
			#instance properties
			self.session_id			 =   session_id
			#add instance to the collector
			Session.instances.setdefault(self.session_id, self)
			#other collectors
			self.connected_surfaces	 =   {}


	#Class methods driven by IDs
	@classmethod
	def check(cls, session_id):
		if session_id in Session.instances:
			return True
		else:
			return False

	@classmethod
	def check_connected_surface(cls, session_id, control_surface_id):
		if Session.check(session_id):
			#Multiple control surfaces with the same ID in the same session are not allowed
			if Session.instances[session_id].connected_surfaces[control_surface_id]:
				return True
			else:
				return False
		else:
			return False

	@classmethod
	def get_connected_surface(cls, session_id, control_surface_id):
		if Session.check_connected_surface(session_id, control_surface_id):
			return Session.instances[session_id].connected_surfaces[control_surface_id]


	#OSC Communication
	def send(self, widget_id, value):
		'''Send the passed value over network to all devices in the same session

		.. versionadded:: 1.0.8
		:attr:`widget_id` it refers to the assigned id of given widget producing the value.
		:attr:`value` can be any type of value accepted from OSC standard.
		'''
		completePath = "/" + str(self.session_id) + "/" + str(widget_id)
		oscAPI.sendMsg(completePath,[value],'0.0.0.0', 57120)							#Broadcast Event

	def set_responder(self, widget_id, opcode, function):
		'''Send the passed value over network to all devices in the same session.

		.. versionadded:: 1.0.8
		:attr:`widget_id` it refers to the assigned id of given widget producing the value.
		:attr:`opcode` is the operation name assigned to the passed function.
		:attr:`function` the definition of function respond.
		'''
		completePath = "/" + str(self.session_id) + "/" + str(widget_id) + "/" + str(opcode)
		oscAPI.bind(Session.osc_listener, function, completePath.strip())				#Broadcast Responder
		Clock.schedule_interval(lambda *x: oscAPI.readQueue(Session.osc_listener), 0)
