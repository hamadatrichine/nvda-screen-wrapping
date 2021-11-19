# screenWrapping
# Copyright 2018 Hamada Trichine, released under GPLv2.

import addonHandler
addonHandler.initTranslation()


def onInstall():
	import wx, api
	# Translators: donation dialog title.
	dialogTitle = _("Would you like to donate?")
	# Translators: donation dialog message.
	ret = wx.MessageBox(_("If you like my work, please consider donating. Any contribution you can give helps me to keep going. My paypal E-mail is hatrichine25@gmail.com. Would you like to copy it to your clipboard? You can always find it under nvda settings/screen wrapping"), dialogTitle, style=wx.YES_NO)
	if ret == wx.YES:
		api.copyToClip("hatrichine25@gmail.com")
