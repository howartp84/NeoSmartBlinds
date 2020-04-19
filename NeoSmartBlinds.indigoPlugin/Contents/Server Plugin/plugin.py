#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

import indigo

import os
import subprocess

import requests

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.


################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", False)
		
		self.baseURL = ""

	########################################

	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		# Since the dialog closed we want to set the debug flag - if you don't directly use
		# a plugin's properties (and for debugLog we don't) you'll want to translate it to
		# the appropriate stuff here.
		if not userCancelled:
			self.debug = valuesDict.get("showDebugInfo", False)
			if self.debug:
				indigo.server.log("Debug logging enabled")
			else:
				indigo.server.log("Debug logging disabled")

	def closedDeviceConfigUi(self, valuesDict, userCancelled, typeId, devId):
		if not userCancelled:
			if (str(typeId) == "controller"):
				dev = indigo.devices[devId]
				devIP = valuesDict["devIP"]
				devPort = valuesDict["devPort"]
				devCtrlID = valuesDict["devCtrlID"]
				dev.stateListOrDisplayStateIdChanged()
				dev.updateStateOnServer("devIP",devIP)
				self.baseURL = str("http://" + devIP + ":" + devPort + "/neo/v1/transmit?command=XYZ" + "&id=" + devCtrlID)
				self.debugLog(self.baseURL)
			if (str(typeId) == "blind"):
				dev = indigo.devices[devId]
				id1 = valuesDict["devID1"]
				id2 = valuesDict["devID2"]
				devCh = valuesDict["devCh"]
				devAddress = str(id1) + "." + str(id2) + "-" + str(devCh)
				dev.stateListOrDisplayStateIdChanged()
				dev.updateStateOnServer("devAddress",devAddress)
		return True

	def deviceStartComm(self, dev):
		#self.debugLog(str(dev.deviceTypeId))
		if (str(dev.deviceTypeId) == "controller"):
			devIP = dev.ownerProps["devIP"]
			devPort = dev.ownerProps["devPort"]
			devCtrlID = dev.ownerProps["devCtrlID"]
			dev.stateListOrDisplayStateIdChanged()
			dev.updateStateOnServer("devIP",devIP)
			self.baseURL = str("http://" + devIP + ":" + devPort + "/neo/v1/transmit?command=XYZ" + "&id=" + devCtrlID)
			self.debugLog(self.baseURL)
			
	def sendCmd(self, pluginAction):
		self.debugLog("sendCmd action called:")
		#self.debugLog(str(pluginAction))
		blindID = pluginAction.deviceId
		blindAddress = indigo.devices[int(blindID)].states["devAddress"]
		
		cmdAction = str(pluginAction.pluginTypeId)

		self.debugLog("Blind: " + str(blindAddress))
		self.debugLog("Action: " + str(cmdAction))

		cmdString = blindAddress + "-" + cmdAction

		cmdURL = self.baseURL.replace("XYZ",cmdString)
		
		self.debugLog("Sending URL: " + str(cmdURL))

		response = requests.get(cmdURL)

		self.debugLog("URL sent was: %s" % response.URL)
		self.debugLog("Controller responded: %s" % response.text)
		
		#self.debugLog(response)
