# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import wx, gui, config

class ScreenWrappingSettings(gui.SettingsPanel):
	# Translators: The name of the addon.
	title = _("Screen Wrapping")

	def makeSettings(self, sizer):
		self.sizer = gui.guiHelper.BoxSizerHelper(self, sizer=sizer)
		# Translators: Text for the check box in the settings that turns on or off the beeps when wrapping.
		self.beepsCheckBox = self.sizer.addItem(wx.CheckBox(self, id=wx.ID_ANY, label=_("&Play a beep when wrapping")))
		self.beepsCheckBox.SetValue(config.conf["screenWrapping"]["turnOnBeeps"])
		
	def onSave(self):
		config.conf["screenWrapping"]["turnOnBeeps"] = self.beepsCheckBox.GetValue()
			
	def onDiscard(self):
		return