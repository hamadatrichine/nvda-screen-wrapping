# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import textInfos, config, re
from documentBase import _Movement
from speech import cancelSpeech
from ui import message
from scriptHandler import willSayAllResume
from . import wrappingAlerts

defaultTranslator = _


def focusAndSpeak(item, direction, readUnit, wrappedAround):
    cancelSpeech()
    if wrappedAround:
        wrappingAlerts.alertWrp(direction)
    item.report(readUnit=readUnit)
    item.moveTo()


def navItersFactory(treeInterceptor, itemType):
    if itemType == "notLinkBlock":
        iterFactory = treeInterceptor._iterNotLinkBlock
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
        iterFactory = lambda direction, info: treeInterceptor._iterNodesByType(
            itemType, direction, info
        )
    return iterFactory


def getWrapAroundItem(treeInterceptor, iterFunc, direction):
    pos = (
        textInfos.POSITION_FIRST
        if direction == _Movement.PREVIOUS
        else textInfos.POSITION_LAST
    )
    direction = _Movement.PREVIOUS if direction == _Movement.NEXT else _Movement.NEXT
    tInfo = treeInterceptor.makeTextInfo(pos)
    it = iterFunc(direction, tInfo)
    lastItem = None
    for elem in it:
        lastItem = elem
    return lastItem


def quickNavWrapping(
    treeInterceptor, gesture, itemType, direction, errorMessage, readUnit
):
    item = None
    wrappedAround = False
    iterFunc = navItersFactory(treeInterceptor, itemType)
    try:
        item = next(iterFunc(direction, treeInterceptor.selection))
    except NotImplementedError:
        message(defaultTranslator("Not supported in this document"))
        return
    except StopIteration:
        item = getWrapAroundItem(treeInterceptor, iterFunc, direction)
        wrappedAround = True
        if not item:
            message(errorMessage)
            return

    if not gesture or not willSayAllResume(gesture):
        focusAndSpeak(item, direction, readUnit, wrappedAround)
