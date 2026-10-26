# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import wx, gui, config, api, addonHandler, webbrowser

addonHandler.initTranslation()

class ScreenWrappingSettings(gui.settingsDialogs.SettingsPanel):
	# Translators: The name of the addon.
	title = _("Screen Wrapping")

	def makeSettings(self, sizer):
		self.sizer = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: Text for the check box in the settings that turns on or off the beeps when wrapping.
		self.beepsCheckBox = self.sizer.addItem(wx.CheckBox(self, id=wx.ID_ANY, label=_("&Play a beep when wrapping")))
		self.beepsCheckBox.SetValue(config.conf["screenWrapping"]["turnOnBeeps"])
		# Translators: Text for the check box in the settings that turns on or off the custom find dialog.
		self.wrapFindDialogCheckBox = self.sizer.addItem(wx.CheckBox(self, id=wx.ID_ANY, label=_("&Enable wrapping functionality for find, requires restart")))
		self.wrapFindDialogCheckBox .SetValue(config.conf["screenWrapping"]["turnOnFindWrap"])
		# Translators: Text for the donations button.
		self.donationButton = self.sizer.addItem(wx.Button(self, id=wx.ID_ANY, label=_("&Buy me a coffee")))
		self.donationButton.Bind(wx.EVT_BUTTON, lambda e: webbrowser.open("https://ko-fi.com/hamadatr"))

	def onSave(self):
		config.conf["screenWrapping"]["turnOnBeeps"] = self.beepsCheckBox.GetValue()
		config.conf["screenWrapping"]["turnOnFindWrap"] = self.wrapFindDialogCheckBox.GetValue()

	def onDiscard(self):
		return