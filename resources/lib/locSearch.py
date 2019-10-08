# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import utils as utils
import json
try:
  import urllib.parse as urlparse
except ImportError:
    import urlparse
try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode
try:
  import urllib.request as urllib2
except ImportError:
    import urllib2
import datetime
import re

class LocSearch():
    UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0"
    locSearchUrl = "https://www.3bmeteo.com/search/search_localita/[TO_SEARCH]/it"
    
    def __init__(self, sProfile, oHandleOrig, sAddonName):
        opener = urllib2.build_opener()
        # Set User-Agent
        opener.addheaders = [('User-Agent', self.UserAgent)]
        urllib2.install_opener(opener)
        self.profileName = sProfile
        self.oHandle = oHandleOrig
        self.addonname = sAddonName
    
    def doSearch(self, locName):
        searchUrl = self.locSearchUrl
        searchUrl = searchUrl.replace("[TO_SEARCH]", locName)
        try:
            response = json.load(urllib2.urlopen(searchUrl))
        except urllib2.HTTPError:
            response = None
            xbmc.executebuiltin('Notification(%s, %s, %d)'%(self.addonname,"Nessuna località trovata per il testo digitato", 5000))
        else:
            if(response):
                for loc in response:
                    liStyle = xbmcgui.ListItem(loc['nome_loc'] + " - " + loc['regione'] + " - "+ loc['stato'] + " - " + loc['prov'])
                    liStyle.setInfo("video", {})
                    utils.addLinkItem({"mode": "setPref", "id_localita": loc['id_localita'], "name_loc": loc['nome_loc']}, self.oHandle, liStyle)
                    xbmc.log(loc['nome_loc'],xbmc.LOGNOTICE)
                xbmcplugin.endOfDirectory(handle=self.oHandle, succeeded=True)

