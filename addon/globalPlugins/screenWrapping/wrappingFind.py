# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import wx
import textInfos
import speech
import controlTypes
from core import callLater
from cursorManager import CursorManager
from gui import guiHelper, messageBox
import addonHandler
from gui.contextHelp import ContextHelpMixin
from . import wrappingAlerts

defaultTranslator = _
addonHandler.initTranslation()


class CustomFindDialog(ContextHelpMixin, wx.Dialog, ):
	helpId = "SearchingForText"
	def __init__(self, parent, cursorManager, text, isCaseSensitive, reverse=False):
		super().__init__(parent=parent, title=defaultTranslator("Find"))
		self.currentCursorManager = cursorManager
		self.reverse = reverse

		dialogSizer = wx.BoxSizer(wx.VERTICAL)
		helperSizer = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		editTextLabel = defaultTranslator("Type the text you wish to find")
		self.findTextField = helperSizer.addLabeledControl(editTextLabel, wx.TextCtrl, value=text)
		self.caseSensitiveCheckBox = wx.CheckBox(self, wx.ID_ANY, label=defaultTranslator("Case &sensitive"))
		self.caseSensitiveCheckBox.SetValue(isCaseSensitive)
		# Translators: An option in the find dialog to allow wrapping on search.
		self.wrapAroundCheckBox = wx.CheckBox(self, wx.ID_ANY, label=_("&Wrap around"))
		self.wrapAroundCheckBox.SetValue(self.currentCursorManager._wrapFind)
		helperSizer.addItem(self.caseSensitiveCheckBox)
		helperSizer.addItem(self.wrapAroundCheckBox)
		helperSizer.addDialogDismissButtons(self.CreateButtonSizer(wx.OK|wx.CANCEL))
		dialogSizer.Add(helperSizer.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		dialogSizer.Fit(self)

		self.SetSizer(dialogSizer)
		self.CentreOnScreen()
		self.SetFocus()
		self.findTextField.SetFocus()

		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)

	def onOk(self, event):
		searchQuery = self.findTextField.GetValue()
		isCaseSensitive = self.caseSensitiveCheckBox.GetValue()
		CursorManager._wrapFind = self.wrapAroundCheckBox.GetValue()
		callLater(100, self.currentCursorManager.doFindText, searchQuery, caseSensitive=isCaseSensitive, reverse=self.reverse)
		self.Destroy()

	def onCancel(self, event):
		self.Destroy()


def speakFindResult(currentCursorManager, textInfoRange, result, willSayAllResume):
	currentCursorManager.selection = textInfoRange
	textInfoRange.move(textInfos.UNIT_LINE,1,endPoint="end")
	if not willSayAllResume:
		speech.speakTextInfo(textInfoRange, reason=controlTypes.OutputReason.CARET)	   

def customDoFindText(cursorManagerInst, text, reverse=False, caseSensitive=False, willSayAllResume=False):
	if not text:
		return
	textInfoRange = cursorManagerInst.makeTextInfo(textInfos.POSITION_CARET)
	result = textInfoRange.find(text, reverse=reverse, caseSensitive=caseSensitive)
	if result:
		speech.cancelSpeech()
		speakFindResult(cursorManagerInst, textInfoRange, result, willSayAllResume)
	else:
		textInfoRange=cursorManagerInst.makeTextInfo(textInfos.POSITION_LAST if reverse else textInfos.POSITION_FIRST)
		result = textInfoRange.find(text,reverse=reverse,caseSensitive=caseSensitive)
		if not cursorManagerInst._wrapFind or not result:
			wx.CallAfter(messageBox, defaultTranslator('text "%s" not found') % text, defaultTranslator("0 matches"), wx.OK|wx.ICON_ERROR)
		else:
			wrappingAlerts.alertWrp(wrappingAlerts.DIRECTION_NEXT if not reverse else wrappingAlerts.DIRECTION_PREV)
			speakFindResult(cursorManagerInst, textInfoRange, result, willSayAllResume)

	CursorManager._lastFindText = text
	CursorManager._lastCaseSensitivity = caseSensitive
