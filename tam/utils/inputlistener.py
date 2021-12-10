# !/usr/bin/env python

import keyboard


class InputListener:

	events_list = {}

	def __init__(self):
		keyboard.hook(self._on_key)
		self.add_event('input', self._input)

	def _on_key(self, event):
		elist = self.events_list
		if (event.event_type == 'down'):
			if (event.name == 'esc') &\
				('exit' in elist):
				elist['exit']()
				keyboard.unhook_all()
			elif (event.name == 'i') &\
				('input' in elist):
				elist['input']()
			else:
				return

	def add_event(self, name: str, event: callable):
		if name and event and name not in self.events_list:
			self.events_list.update({name: event})

	def _input(self):
		elist = self.events_list
		istring = input()
		if (istring in ['stop', 'exit', 'quit']) & ('exit' in elist):
			elist['exit']()
