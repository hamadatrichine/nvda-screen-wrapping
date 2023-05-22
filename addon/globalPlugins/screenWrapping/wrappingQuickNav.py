# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import textInfos
from core import callLater
from ui import message
from scriptHandler import willSayAllResume
from speech import cancelSpeech
from tones import beep
from . import wrappingAlerts

import addonHandler
addonHandler.initTranslation()


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

def screenWrapping(treeInterceptor, itemType, readUnit, wrp2, reverse="previous", direction="next"):
	updatePosition(treeInterceptor, wrp2)
	navItems = initNavItemsGenerator(treeInterceptor, itemType)
	try:
		wrapping = next(navItems(direction, treeInterceptor.selection))
		wrappingAlerts.alertWrp(direction)
		wrapping.moveTo()
		try:
			wrapping = next(navItems(reverse, treeInterceptor.selection))
			callLater(300,wrapping.moveTo)
		except StopIteration:
			pass
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
			if not screenWrapping(treeInterceptor, itemType, readUnit, wrp2=textInfos.POSITION_FIRST):
				resetPosition(treeInterceptor, lastPos, errorMessage)
		else:
			lastPos = getCurrentPos(treeInterceptor)
			if not screenWrapping(treeInterceptor, itemType, readUnit, wrp2=textInfos.POSITION_LAST, reverse="next", direction="previous"):
				resetPosition(treeInterceptor, lastPos, errorMessage)
		return

	item.moveTo()
	if not gesture or not willSayAllResume(gesture):
		item.report(readUnit=readUnit)