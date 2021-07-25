# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "screenWrapping",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("screen wrapping for nvda"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("""This addon brings the screen wrapping feature to nvda.
	When you press quick navigation keys such as h, b, f and others, you will be placed on the next element regardless of your current position on a webpage.
	If elements are not found below your position, you will be placed at the first element of the requested type available from the beginning of the page and virseversa when you are searching upwards."""),
	# version
	"addon_version" : "1.6",
	# Author(s)
	"addon_author" : u"Hamada Trichine <hamadalog25@gmail.com>",
	# URL for the add-on documentation support
	"addon_url" : "https://github.com/hamadatrichine/nvda-screen-wrapping",
	# Documentation file name
	"addon_docFileName" : "readme.html",
	"addon_nvdaMinimumVersion" : "2021.1",
	"addon_lastTestedNvdaVersion" : "2021.1",
	"addon_updateChannel" : None,
}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [os.path.join("addon", "globalPlugins", "screenWrapping", "*.py")]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []
