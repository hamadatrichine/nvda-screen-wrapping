# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import textInfos, config, re
from documentBase import _Movement
from core import callLater
from ui import message
from scriptHandler import willSayAllResume
from speech import cancelSpeech
from tones import beep
from . import wrappingAlerts

defaultTranslator = _

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
		iterFactory=treeInterceptor._iterNotLinkBlock
	elif itemType == "textParagraph":
		punctuationMarksRegex = re.compile(
			config.conf["virtualBuffers"]["textParagraphRegex"],
		)

		def paragraphFunc(info):
			return punctuationMarksRegex.search(info.text) is not None

		def iterFactory(direction, pos):
			return treeInterceptor._iterSimilarParagraph(
				kind="textParagraph",
				paragraphFunction=paragraphFunc,
				desiredValue=True,
				direction=_Movement(direction),
				pos=pos,
			)
	elif itemType == "verticalParagraph":
		def paragraphFunc(info):
			try:
				return info.location[0]
			except (AttributeError, TypeError):
				return None

		def iterFactory(direction, pos):
			return treeInterceptor._iterSimilarParagraph(
				kind="verticalParagraph",
				paragraphFunction=paragraphFunc,
				desiredValue=None,
				direction=_Movement(direction),
				pos=pos,
			)
	elif itemType in ["sameStyle", "differentStyle"]:
		def iterFactory(direction, info):
			return treeInterceptor._iterTextStyle(itemType, direction, info)
	else:
		iterFactory=lambda direction,info: treeInterceptor._iterNodesByType(itemType,direction,info)
	return iterFactory

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
		message(defaultTranslator("Not supported in this document"))
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