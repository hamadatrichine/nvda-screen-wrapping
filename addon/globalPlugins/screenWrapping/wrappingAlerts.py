# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import config
from speech import cancelSpeech
from ui import message
from tones import beep


DIRECTION_NEXT = "next"
DIRECTION_PREV = "previous"

def playBeep(hz, length):
	if config.conf["screenWrapping"]["turnOnBeeps"]:
		beep(hz, length)

def alertWrp(direction):
	cancelSpeech()
	if direction == DIRECTION_PREV:
		# Translators: Text spoken when screen wrapping to bottom.
		message(_("wrapping to bottom"))
		playBeep(100, 80)
	else:
		# Translators: Text spoken when screen wrapping to top.
		message(_("wrapping to top"))
		playBeep(500, 80)

def alertToggleFunctionality(state):
	if state:
		message(
			# Translators: Text spoken when screen rapping is turned off.
			_("Screen wrapping off."))
		playBeep(100,150)
	else:
		message(
			# Translators: Text spoken when screen rapping is turned on.
			_("Screen wrapping on."))
		playBeep(400,150)