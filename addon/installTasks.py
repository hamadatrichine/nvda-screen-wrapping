# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import webbrowser
import addonHandler
addonHandler.initTranslation()


def onInstall():
	import wx, api
	# Translators: donation dialog title.
	dialogTitle = _("Would you like to donate?")
	# Translators: donation dialog message.
	ret = wx.MessageBox(_("If you like my work, please consider buying me a coffee. You can always find this option under nvda settings/screen wrapping"), dialogTitle, style=wx.YES_NO)
	if ret == wx.YES:
		webbrowser.open("https://ko-fi.com/hamadatr")
