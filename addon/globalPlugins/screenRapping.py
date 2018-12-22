# screenRapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

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
from scriptHandler import willSayAllResume

addonHandler.initTranslation()

confspec = {'isActive':'boolean(default=True)'}
config.conf.spec['screenrapping'] = confspec

oldQuickNav = BrowseModeTreeInterceptor._quickNavScript

# Text to translate
# Translators: Text spoken when screen rapping to top.
msgrpTop = _('rapping to top')
# Translators: Text spoken when screen rapping to bottom.
msgrpBottom = _('rapping to bottom')

def getCurrentPos(self):
	currentPosStart = self.makeTextInfo(textInfos.POSITION_FIRST)
	currentPosEnd = self.makeTextInfo(textInfos.POSITION_CARET)
	currentPosStart.setEndPoint(currentPosEnd, 'endToStart')
	return len(currentPosStart.text)

def resetPosition(self, positionNumber,itemType):
	pos = self.makeTextInfo(textInfos.POSITION_FIRST)
	pos.move(textInfos.UNIT_CHARACTER, positionNumber)
	if hasattr(self, 'selection'):
		self.selection = pos
	else:
		pos.updateCaret()
	cancelSpeech()
	pos.move(textInfos.UNIT_LINE,1,endPoint="end")
	itemText = '{}s'.format(itemType) if itemType[-1] != 'x' else '{}es'.format(itemType)
	message(
			# translators: Text spoken when the type of nav items does not exist in the page.
			_('No {} in this page.'.format(itemText)))

def updatePosition(obj,position):
	objPos = obj.makeTextInfo(position)
	objPos.updateCaret()
	cancelSpeech()

def initNavItemsGenerator(self,itemType):
	if itemType=="notLinkBlock":
		return self._iterNotLinkBlock
	else:
		return lambda direction,info: self._iterNodesByType(itemType,direction,info)

def screenRapping(self,itemType,readUnit,msg,rpTo,tone=(500,80),reverse='previous',direction='next'):
	updatePosition(self,rpTo)
	navItems = initNavItemsGenerator(self,itemType)
	try:
		rapping = next(navItems(direction,self.selection))
		speak([msg])
		rapping.moveTo()
		try:
			rapping = next(navItems(reverse,self.selection))
			callLater(300,rapping.moveTo)
		except StopIteration:
			pass
		beep(tone[0],tone[1])
		rapping.report(readUnit=readUnit)
		return True
	except StopIteration:
		pass

def quickNavRapping(self,gesture, itemType, direction, errorMessage, readUnit):
	iterFactory = initNavItemsGenerator(self,itemType)
	try:
		item = next(iterFactory(direction, self.selection))
	except NotImplementedError:
		# Translators: a message when a particular quick nav command is not supported in the current document.
		message(_('Not supported in this document'))
		return
	except StopIteration:
		if direction == 'next':
			lastPos = getCurrentPos(self)
			if not screenRapping(self,itemType,readUnit,msgrpTop,rpTo=textInfos.POSITION_FIRST):
				resetPosition(self,lastPos,itemType)
		else:
			lastPos = getCurrentPos(self)
			if not screenRapping(self,itemType,readUnit,msgrpBottom,rpTo=textInfos.POSITION_LAST,tone=(100,80),reverse='next',direction='previous'):
				resetPosition(self,lastPos,itemType)
		return

	item	.moveTo()
	if not gesture or not willSayAllResume(gesture):
		item.report(readUnit=readUnit)


class GlobalPlugin(GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		global oldQuickNav
		self.isActivated = config.conf['screenrapping']['isActive']
		if self.isActivated: BrowseModeTreeInterceptor._quickNavScript = quickNavRapping

	def script_toggleScreenRapping(self, gesture):
		if self.isActivated:
			BrowseModeTreeInterceptor._quickNavScript = oldQuickNav
			config.conf['screenrapping']['isActive'] = False
			self.isActivated = config.conf['screenrapping']['isActive']
			message(
					# Translators: Text spoken when screen rapping is turned off.
					_('Screen rapping off.'))
			beep(100,150)
		else:
			BrowseModeTreeInterceptor._quickNavScript = quickNavRapping
			config.conf['screenrapping']['isActive'] = True
			self.isActivated = config.conf['screenrapping']['isActive']
			message(
					# Translators: Text spoken when screen rapping is turned on.
					_('Screen rapping on.'))
			beep(400,150)

	# Translators: A discription for the toggaleScreenRapping script.
	script_toggleScreenRapping.__doc__ = _('Activates and deactivates the screen rapping feature.')
	script_toggleScreenRapping.category = SCRCAT_BROWSEMODE

	def terminate(self):
		BrowseModeTreeInterceptor._quickNavScript = oldQuickNav

	__gestures = {
		'KB:NVDA+H':'toggleScreenRapping'
	}
