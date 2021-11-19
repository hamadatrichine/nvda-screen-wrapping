# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import wx, gui, config, api

class ScreenWrappingSettings(gui.SettingsPanel):
	# Translators: The name of the addon.
	title = _("Screen Wrapping")

	def makeSettings(self, sizer):
		self.sizer = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: Text for the check box in the settings that turns on or off the beeps when wrapping.
		self.beepsCheckBox = self.sizer.addItem(wx.CheckBox(self, id=wx.ID_ANY, label=_("&Play a beep when wrapping")))
		self.beepsCheckBox.SetValue(config.conf["screenWrapping"]["turnOnBeeps"])
		# Translators: Text for the button in the settings that copys the donation E-mail to the clipboard.
		self.copyDonationMailButton = self.sizer.addItem(wx.Button(self, id=wx.ID_ANY, label=_("&Copy PayPal donation E-mail to clipboard")))
		self.copyDonationMailButton.Bind(wx.EVT_BUTTON, lambda e: api.copyToClip("hatrichine25@gmail.com"))

	def onSave(self):
		config.conf["screenWrapping"]["turnOnBeeps"] = self.beepsCheckBox.GetValue()

	def onDiscard(self):
		return