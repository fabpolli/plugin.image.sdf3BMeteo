# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import utils as utils

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

class ManageData:
    UserAgent = "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-I9105P Build/JDQ39)"
    meteoDataUrl = "https://www.3bmeteo.com/moduli_esterni/localita_7_giorni_orario/[LOC_CODE]/ffffff/0080ff/5e5e5e/ffffff/it#page=[PAGE_NO]"
    profileName = ""
    oHandle = -1
    
    def __init__(self, sProfile, oHandleOrig):
        opener = urllib2.build_opener()
        # Set User-Agent
        opener.addheaders = [('User-Agent', self.UserAgent)]
        urllib2.install_opener(opener)
        self.profileName = sProfile
        self.oHandle = oHandleOrig
    
    def getSingleInfo(self, sText):
        sTimeSection = re.findall('<div class="time">([^<]+?)</div>', sText)
        sIconSection = re.findall(r'url\(["\']?(?P<url>[^"\']+)["\']?\)', sText)
        sTempSection = re.findall('<p>([^<]+?)</p>', sText)
        sTempOut = sTempSection[0]
        sTempOut = sTempOut.replace("&deg;",'°')
        return (sTimeSection[0], sTempOut, sIconSection[0])

    def getUrl(self, pathId):
            pathId = pathId.replace(" ", "%20")
            if pathId[0:2] == "//":
                url = "https:" + pathId
            else:
                url = pathId
            return url

    def show_day_forecast(self, page, locCode):
        url = self.meteoDataUrl
        url = url.replace("[PAGE_NO]", page)
        url = url.replace("[LOC_CODE]", locCode)
        #xbmc.log(url,xbmc.LOGNOTICE)
        sHtml = urllib2.urlopen(url).read()
        oPage = re.findall('<div id="page-.*', sHtml)
        nPage = int(page[-1:])
        if(oPage):
            sections = re.findall('(<div class="day_container".*?</p>)', oPage[nPage])
            for subSection in sections:
                aInfo = self.getSingleInfo(subSection)
                imageUrl = self.getUrl(aInfo[2])
                filename = imageUrl[imageUrl.rfind("/")+1:]
                bigImageUrl = imageUrl.replace("loc_small_jpg", "loc_big_jpg")
                bigFileName = "big_" + imageUrl[imageUrl.rfind("/")+1:]
                if(not os.path.isfile(self.profileName + filename)):
                    imgRequest = urllib2.Request(imageUrl)
                    imgData = urllib2.urlopen(imgRequest).read()
                    output = open(self.profileName + filename,'wb')
                    output.write(imgData)
                    output.close()
                    imgRequest = urllib2.Request(bigImageUrl)
                    imgData = urllib2.urlopen(imgRequest).read()
                    output = open(self.profileName + bigFileName,'wb')
                    output.write(imgData)
                    output.close()
                icon = self.profileName+ bigFileName
                thumbnail = self.profileName + filename
                liStyle = xbmcgui.ListItem(" " + aInfo[0] + " [B]" + aInfo[1] + "[/B]")
                liStyle.setArt({'thumb': icon, 'icon': icon})
                liStyle.setInfo("video", {})
                utils.addLinkItem({"mode": "nop"}, self.oHandle, liStyle)
        xbmcplugin.endOfDirectory(handle=self.oHandle, succeeded=True)