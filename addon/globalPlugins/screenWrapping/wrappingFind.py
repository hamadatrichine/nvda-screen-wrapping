# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import weakref
import wx
import textInfos
import speech
import controlTypes
import addonHandler
import config
from core import callLater
from cursorManager import CursorManager
from gui import guiHelper, messageBox
from gui.contextHelp import ContextHelpMixin
from . import wrappingAlerts

defaultTranslator = _
addonHandler.initTranslation()


class CustomFindDialog(
	ContextHelpMixin,
	wx.Dialog,  # wxPython does not seem to call base class initializer, put last in MRO
):
	"""A dialog used to specify text to find in a cursor manager.

	Only one instance can exist at a time.
	Creating a dialog while another one is still open returns that dialog,
a	retargeted at the newly provided cursor manager and search parameters.
	"""

	helpId = "SearchingForText"

	shouldSuspendConfigProfileTriggers = True

	_instance: "weakref.ReferenceType[CustomFindDialog] | None" = None

	def __new__(cls, *args, **kwargs):
		# Make this a singleton.
		# A dialog whose underlying window has been destroyed is falsy, so a new instance is created instead.
		inst = cls._instance() if cls._instance else None
		if not inst:
			return super().__new__(cls)
		return inst

	def __init__(
		self,
		parent: wx.Window,
		cursorManager: "CursorManager",
		text: str,
		caseSensitivity: bool,
		reverse: bool = False,
		searchEntries: list[str] | None = None,
	):
		"""
		:param parent: The parent window for this dialog.
		:param cursorManager: The cursor manager to perform the search in.
		:param text: The initial text of the search field.
		:param caseSensitivity: The initial state of the case sensitivity check box.
		:param reverse: Whether to search backwards from the caret.
		:param searchEntries: Previously searched terms to offer in the search field,
			most-recent first. Only used when the search history setting is enabled.
		"""
		inst = CustomFindDialog._instance() if CustomFindDialog._instance else None
		if inst:
			self._retarget(cursorManager, text, caseSensitivity, reverse, searchEntries)
			return
		# Use a weakref so the instance can die.
		CustomFindDialog._instance = weakref.ref(self)
		# Translators: Title of a dialog to find text.
		super().__init__(parent, title=defaultTranslator("Find"))

		# Have a copy of the active cursor manager, as this is needed later for finding text.
		self.activeCursorManager = cursorManager
		self.reverse = reverse
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Dialog text for NvDA's find command.
		findLabelText = defaultTranslator("Type the text you wish to find")
		if config.conf["virtualBuffers"]["findHistory"]:
			self.findTextField = sHelper.addLabeledControl(
				findLabelText,
				wx.ComboBox,
				choices=searchEntries or [],
				value=text,
				style=wx.CB_DROPDOWN,
			)
		else:
			self.findTextField = sHelper.addLabeledControl(findLabelText, wx.TextCtrl, value=text)
		# Translators: An option in find dialog to perform case-sensitive search.
		self.caseSensitiveCheckBox = wx.CheckBox(self, wx.ID_ANY, label=defaultTranslator("Case &sensitive"))
		self.caseSensitiveCheckBox.SetValue(caseSensitivity)
		# Translators: An option in the find dialog to allow wrapping on search.
		self.wrapAroundCheckBox = wx.CheckBox(self, wx.ID_ANY, label=_("&Wrap around"))
		self.wrapAroundCheckBox.SetValue(CursorManager._wrapFind)
		sHelper.addItem(self.caseSensitiveCheckBox)
		sHelper.addItem(self.wrapAroundCheckBox)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.CentreOnScreen()
		self.findTextField.SetFocus()

	def _retarget(
		self,
		cursorManager: "CursorManager",
		text: str,
		caseSensitivity: bool,
		reverse: bool,
		searchEntries: list[str] | None,
	) -> None:
		"""Point this dialog at another search request.

		Called when the find command is executed while this dialog is still open,
		possibly from a different document than the one it was opened for.

		:param cursorManager: The cursor manager to perform the search in.
		:param text: The text of the search field.
		:param caseSensitivity: The state of the case sensitivity check box.
		:param reverse: Whether to search backwards from the caret.
		:param searchEntries: Previously searched terms to offer in the search field, most-recent first.
		"""
		self.activeCursorManager = cursorManager
		self.reverse = reverse
		self.caseSensitiveCheckBox.SetValue(caseSensitivity)
		self.wrapAroundCheckBox.SetValue(CursorManager._wrapFind)
		if isinstance(self.findTextField, wx.ComboBox):
			# Setting the choices clears the value, so restore it afterwards.
			self.findTextField.Set(searchEntries or [])
		self.findTextField.SetValue(text)
		self.findTextField.SelectAll()

	def onOk(self, evt):
		text = self.findTextField.GetValue()
		caseSensitive = self.caseSensitiveCheckBox.GetValue()
		CursorManager._wrapFind = self.wrapAroundCheckBox.GetValue()
		# We must use core.callLater rather than wx.CallLater to ensure that the callback runs within NVDA's core pump.
		# If it didn't, and it directly or indirectly called wx.Yield, it could start executing NVDA's core pump from within the yield, causing recursion.
		callLater(
			100,
			self.activeCursorManager.doFindText,
			text,
			caseSensitive=caseSensitive,
			reverse=self.reverse,
		)
		self.Destroy()

	def onCancel(self, evt):
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
		lastResult = False
		currentResult = lastResult
		if cursorManagerInst._wrapFind:
			textInfoRange=cursorManagerInst.makeTextInfo(textInfos.POSITION_ALL)
			textInfoRange.collapse(end=True)

			currentResult = textInfoRange.find(text,reverse=True,caseSensitive=caseSensitive)
			lastResult = currentResult
			while currentResult and not reverse:
				lastResult = currentResult
				currentResult = textInfoRange.find(text,reverse=True,caseSensitive=caseSensitive)

		if not cursorManagerInst._wrapFind or not lastResult:
			wx.CallAfter(messageBox, defaultTranslator('text "%s" not found') % text, defaultTranslator("0 matches"), wx.OK|wx.ICON_ERROR)
		else:
			wrappingAlerts.alertWrp(wrappingAlerts.DIRECTION_NEXT if not reverse else wrappingAlerts.DIRECTION_PREV)
			speakFindResult(cursorManagerInst, textInfoRange, lastResult, willSayAllResume)

	CursorManager._lastFindText = text
	CursorManager._lastCaseSensitivity = caseSensitive
