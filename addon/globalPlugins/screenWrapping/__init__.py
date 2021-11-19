# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import addonHandler
import config
import gui
import cursorManager
from globalPluginHandler import GlobalPlugin
from browseMode import BrowseModeTreeInterceptor
from inputCore import SCRCAT_BROWSEMODE
from ui import message
from scriptHandler import script
from . import wrappingFind, wrappingQuickNav, wrappingAlerts, wrappingSettingsGui

addonHandler.initTranslation()

confspec = {"isActive":"boolean(default=True)", "turnOnBeeps":"boolean(default=True)"}
config.conf.spec["screenWrapping"] = confspec


class GlobalPlugin(GlobalPlugin):
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(wrappingSettingsGui.ScreenWrappingSettings)
		self.oldQuickNav = BrowseModeTreeInterceptor._quickNavScript
		self.oldFindDialog = cursorManager.FindDialog
		self.oldFindBackend = cursorManager.CursorManager.doFindText
		self.isActivated = config.conf["screenWrapping"]["isActive"]
		if self.isActivated:
			self.patch()

	def patch(self):
		BrowseModeTreeInterceptor._quickNavScript = wrappingQuickNav.quickNavWrapping
		cursorManager.CursorManager.doFindText = wrappingFind.customDoFindText
		setattr(cursorManager.CursorManager, '_wrapFind', True)
		cursorManager.FindDialog = wrappingFind.CustomFindDialog	

	def clean(self):
		BrowseModeTreeInterceptor._quickNavScript = self.oldQuickNav
		cursorManager.CursorManager.doFindText = self.oldFindBackend
		cursorManager.FindDialog = self.oldFindDialog
		setattr(cursorManager.CursorManager, '_wrapFind', None)

	@script(
		# Translators: A discription for the toggleScreenWrapping script.
		description=_("Activates and deactivates the screen wrapping feature."),
		category = SCRCAT_BROWSEMODE,
		gesture = "KB:NVDA+H"
	)
	def script_toggleScreenWrapping(self, gesture):
		if self.isActivated:
			self.clean()
			config.conf["screenWrapping"]["isActive"] = False
			self.isActivated = config.conf["screenWrapping"]["isActive"]
		else:
			self.patch()
			config.conf["screenWrapping"]["isActive"] = True
			self.isActivated = config.conf["screenWrapping"]["isActive"]

		wrappingAlerts.alertToggleFunctionality(not self.isActivated)

	def terminate(self):
		self.clean()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(wrappingSettingsGui.ScreenWrappingSettings)
