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
msgrpTop = _("wrapping to top")
# Translators: Text spoken when screen wrapping to bottom.
msgrpBottom = _("wrapping to bottom")

def getCurrentPos(self):
	currentPosStart = self.makeTextInfo(textInfos.POSITION_FIRST)
	currentPosEnd = self.makeTextInfo(textInfos.POSITION_CARET)
	currentPosStart.setEndPoint(currentPosEnd, "endToStart")
	return len(currentPosStart.text)

def resetPosition(self, positionNumber,itemType):
	pos = self.makeTextInfo(textInfos.POSITION_FIRST)
	pos.move(textInfos.UNIT_CHARACTER, positionNumber)
	if hasattr(self, "selection"):
		self.selection = pos
	else:
		pos.updateCaret()
	cancelSpeech()
	pos.move(textInfos.UNIT_LINE,1,endPoint="end")
	itemText = '{}s'.format(itemType) if itemType[-1] != 'x' else '{}es'.format(itemType)
	message(
			# translators: Text spoken when the type of nav items does not exist in the page.
			_("No {} in this page").format(itemText))

def updatePosition(obj,position):
	objPos = obj.makeTextInfo(position)
	objPos.updateCaret()
	cancelSpeech()

def initNavItemsGenerator(self,itemType):
	if itemType=="notLinkBlock":
		return self._iterNotLinkBlock
	else:
		return lambda direction,info: self._iterNodesByType(itemType,direction,info)

def screenWrapping(self,itemType,readUnit,msg,rpTo,tone=(500,80),reverse="previous", direction="next"):
	updatePosition(self,rpTo)
	navItems = initNavItemsGenerator(self,itemType)
	try:
		wrapping = next(navItems(direction,self.selection))
		speak([msg])
		wrapping.moveTo()
		try:
			wrapping = next(navItems(reverse,self.selection))
			callLater(300,wrapping.moveTo)
		except StopIteration:
			pass
		beep(tone[0],tone[1])
		wrapping.report(readUnit=readUnit)
		return True
	except StopIteration:
		pass

def quickNavWrapping(self,gesture, itemType, direction, errorMessage, readUnit):
	iterFactory = initNavItemsGenerator(self,itemType)
	try:
		item = next(iterFactory(direction, self.selection))
	except NotImplementedError:
		# Translators: a message when a particular quick nav command is not supported in the current document.
		message(_("Not supported in this document"))
		return
	except StopIteration:
		if direction == "next":
			lastPos = getCurrentPos(self)
			if not screenWrapping(self,itemType,readUnit,msgrpTop,rpTo=textInfos.POSITION_FIRST):
				resetPosition(self,lastPos,itemType)
		else:
			lastPos = getCurrentPos(self)
			if not screenWrapping(self,itemType,readUnit,msgrpBottom,rpTo=textInfos.POSITION_LAST,tone=(100,80),reverse="next", direction="previous"):
				resetPosition(self,lastPos,itemType)
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

