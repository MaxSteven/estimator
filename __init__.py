# -*- coding: utf-8 -*-
# --------------------------------------------------------------
# Estimator: calculate space occupied by files presented in script
#
# Andrew Savchenko © 2015
# andrew@savchenko.net
#
# Attribution 4.0 International (CC BY 4.0)
# https://creativecommons.org/licenses/by/4.0/
#
# Developed on OSX, should work on random *nix system
# --------------------------------------------------------------
__version__ = "0.1.2"
__release__ = True

import nuke
import nukescripts

if nuke.GUI:
    from estimator_panel import estimatorPanel
    def addPanel():
        return estimatorPanel().addToPane()

if nuke.GUI:
    menu = nuke.menu("Pane")
    menu.addCommand("Estimator", addPanel)
    nukescripts.registerPanel(
        "uk.co.thefoundry.estimatorPanel", addPanel)
