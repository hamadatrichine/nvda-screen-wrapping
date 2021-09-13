# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import api
import addonHandler
import config
import textInfos
from globalPluginHandler import GlobalPlugin
from browseMode import BrowseModeTreeInterceptor
from core import callLater
from inputCore import SCRCAT_BROWSEMODE
from ui import message
from tones import beep
from speech import cancelSpeech, speak
from scriptHandler import script, willSayAllResume

addonHandler.initTranslation()

confspec = {"isActive":"boolean(default=True)"}
config.conf.spec["screenWrapping"] = confspec

oldQuickNav = BrowseModeTreeInterceptor._quickNavScript

# Text to translate
# Translators: Text spoken when screen wrapping to top.
msgwrpTop = _("wrapping to top")
# Translators: Text spoken when screen wrapping to bottom.
msgwrpBottom = _("wrapping to bottom")

def getCurrentPos(treeInterceptor):
	posDelta = treeInterceptor.makeTextInfo(textInfos.POSITION_FIRST)
	posDelta.setEndPoint(treeInterceptor.makeTextInfo(textInfos.POSITION_CARET), "endToStart")
	return len(posDelta.text)

def resetPosition(treeInterceptor, offset, errorMessage):
	cursor = treeInterceptor.makeTextInfo(textInfos.POSITION_FIRST)
	cursor.move(textInfos.UNIT_CHARACTER, offset)
	if hasattr(treeInterceptor, "selection"):
		treeInterceptor.selection = cursor
	else:
		cursor.updateCaret()
	cancelSpeech()
	cursor.move(textInfos.UNIT_LINE,1,endPoint="end")
	message(errorMessage)

def updatePosition(treeInterceptor, position):
	cursor = treeInterceptor.makeTextInfo(position)
	cursor.updateCaret()
	cancelSpeech()

def initNavItemsGenerator(treeInterceptor, itemType):
	if itemType=="notLinkBlock":
		return treeInterceptor._iterNotLinkBlock
	else:
		return lambda direction, info: treeInterceptor._iterNodesByType(itemType, direction, info)

def screenWrapping(treeInterceptor, itemType, readUnit, msg, wrp2, tone=(500,80), reverse="previous", direction="next"):
	updatePosition(treeInterceptor, wrp2)
	navItems = initNavItemsGenerator(treeInterceptor, itemType)
	try:
		wrapping = next(navItems(direction, treeInterceptor.selection))
		speak([msg])
		wrapping.moveTo()
		try:
			wrapping = next(navItems(reverse, treeInterceptor.selection))
			callLater(300,wrapping.moveTo)
		except StopIteration:
			pass
		beep(tone[0],tone[1])
		wrapping.report(readUnit=readUnit)
		return True
	except StopIteration:
		pass

def quickNavWrapping(treeInterceptor, gesture, itemType, direction, errorMessage, readUnit):
	iterFactory = initNavItemsGenerator(treeInterceptor, itemType)
	try:
		item = next(iterFactory(direction, treeInterceptor.selection))
	except NotImplementedError:
		# Translators: a message when a particular quick nav command is not supported in the current document.
		message(_("Not supported in this document"))
		return
	except StopIteration:
		if direction == "next":
			lastPos = getCurrentPos(treeInterceptor)
			if not screenWrapping(treeInterceptor, itemType, readUnit, msgwrpTop, wrp2=textInfos.POSITION_FIRST):
				resetPosition(treeInterceptor, lastPos, errorMessage)
		else:
			lastPos = getCurrentPos(treeInterceptor)
			if not screenWrapping(treeInterceptor, itemType, readUnit, msgwrpBottom, wrp2=textInfos.POSITION_LAST, tone=(100,80), reverse="next", direction="previous"):
				resetPosition(treeInterceptor, lastPos, errorMessage)
		return

	item.moveTo()
	if not gesture or not willSayAllResume(gesture):
		item.report(readUnit=readUnit)


class GlobalPlugin(GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		global oldQuickNav
		self.isActivated = config.conf["screenWrapping"]["isActive"]
		if self.isActivated:
			BrowseModeTreeInterceptor._quickNavScript = quickNavWrapping


	@script(
		# Translators: A discription for the toggleScreenWrapping script.
		description=_("Activates and deactivates the screen wrapping feature."),
		category = SCRCAT_BROWSEMODE,
		gesture = "KB:NVDA+H"
	)
	def script_toggleScreenWrapping(self, gesture):
		if self.isActivated:
			BrowseModeTreeInterceptor._quickNavScript = oldQuickNav
			config.conf["screenWrapping"]["isActive"] = False
			self.isActivated = config.conf["screenWrapping"]["isActive"]
			message(
					# Translators: Text spoken when screen rapping is turned off.
					_("Screen wrapping off."))
			beep(100,150)
		else:
			BrowseModeTreeInterceptor._quickNavScript = quickNavWrapping
			config.conf["screenWrapping"]["isActive"] = True
			self.isActivated = config.conf["screenWrapping"]["isActive"]
			message(
					# Translators: Text spoken when screen rapping is turned on.
					_("Screen wrapping on."))
			beep(400,150)

	def terminate(self):
		BrowseModeTreeInterceptor._quickNavScript = oldQuickNav

