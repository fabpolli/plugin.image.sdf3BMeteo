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
from bs4 import BeautifulSoup
#import web_pdb

class ManageData:
    UserAgent = "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-I9105P Build/JDQ39)"
    meteoDataUrl = "https://www.3bmeteo.com/moduli_esterni/localita_7_giorni_orario/[LOC_CODE]/ffffff/0080ff/5e5e5e/ffffff/it#page=[PAGE_NO]"
    meteoDataUrlDI = "http://www.3bmeteo.com/meteo/[LOC_NAME]"
    meteoDataUrlDI_ND = "http://www.3bmeteo.com/meteo/[LOC_NAME]/dettagli_orari/[DAY_NO]"
    aMeteoMoreData = [{},{},{},{},{},{},{},{}]
    profileName = ""
    oHandle = -1
    
    def __init__(self, sProfile, oHandleOrig):
        opener = urllib2.build_opener()
        # Set User-Agent
        opener.addheaders = [('User-Agent', self.UserAgent)]
        urllib2.install_opener(opener)
        self.profileName = sProfile
        self.oHandle = oHandleOrig

    def getUrl(self, pathId):
            pathId = pathId.replace(" ", "%20")
            if pathId[0:2] == "//":
                url = "https:" + pathId
            else:
                url = pathId
            return url

    def save_image_to_disk(self, filename, imageUrl, bigFileName, bigImageUrl):
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
            
    def show_day_forecast(self, page, locCode, locName):
        #web_pdb.set_trace()
        url = self.meteoDataUrl
        nIdxPage = int(page.split('-')[1])
        url = url.replace("[PAGE_NO]", page)
        url = url.replace("[LOC_CODE]", str(locCode))
        #xbmc.log(url,xbmc.LOGNOTICE)
        sHtml = urllib2.urlopen(url).read()
        soup = BeautifulSoup(sHtml, 'html.parser')
        pageDiv =soup.find('div', {"id": page})
        mydivs =pageDiv.find_all('div', {"class": "day_container"})
        for singleDiv in mydivs:
            sStyleUrl=singleDiv.find('div',{"class": ["simbolo", "limiter"]})
            sIconSection = re.findall(r'url\(["\']?(?P<url>[^"\']+)["\']?\)', sStyleUrl["style"])
            imageUrl=self.getUrl(sIconSection[0])
            filename = imageUrl[imageUrl.rfind("/")+1:]
            bigImageUrl = imageUrl.replace("loc_small_jpg", "loc_big_jpg")
            bigFileName = "big_" + imageUrl[imageUrl.rfind("/")+1:]
            sHour=singleDiv.find('div',{"class": "time"}).getText()
            sTemp=singleDiv.find('div',{"class": "desc"}).getText().strip().encode("utf-8")
            nHour=int(sHour.split(':')[0])
            self.aMeteoMoreData[nIdxPage][nHour]={"d": "", "tp":"", "p":"", "t": sTemp, "u":"", "in": filename, "iu": imageUrl, "bin": bigFileName, "biu": bigImageUrl}
        #Get extended data selected day and previous day if selected day is after today
        self.get_meteo_data(locName, nIdxPage)
        if(nIdxPage>0):
            self.get_meteo_data(locName, nIdxPage-1)
        
        for dData in self.aMeteoMoreData[nIdxPage]:
            self.save_image_to_disk(self.aMeteoMoreData[nIdxPage][dData]["in"], self.aMeteoMoreData[nIdxPage][dData]["iu"], self.aMeteoMoreData[nIdxPage][dData]["bin"], self.aMeteoMoreData[nIdxPage][dData]["biu"])
            if not self.aMeteoMoreData[nIdxPage][dData]["d"]:
                sItemText = "{0:02d}:00 [B]{1}[/B]".encode("utf-8")
            else:
                if((not self.aMeteoMoreData[nIdxPage][dData]["p"]) or (self.aMeteoMoreData[nIdxPage][dData]["p"]=="assenti")) :
                    sItemText = u"{0:02d}:00 {2} [B]{1}°C[/B] ({3}°C) umidità {4}%".encode("utf-8")
                else:
                    sItemText = u"{0:02d}:00 {2} {5}mm [B]{1}°C[/B] ({3}°C) umidità {4}%".encode("utf-8")
            sItemText = sItemText.format(dData, self.aMeteoMoreData[nIdxPage][dData]["t"], self.aMeteoMoreData[nIdxPage][dData]["d"], self.aMeteoMoreData[nIdxPage][dData]["tp"], self.aMeteoMoreData[nIdxPage][dData]["u"], self.aMeteoMoreData[nIdxPage][dData]["p"])
            liStyle = xbmcgui.ListItem(sItemText)
            icon = self.profileName+ self.aMeteoMoreData[nIdxPage][dData]["bin"]
            liStyle.setArt({'thumb': icon, 'icon': icon})
            liStyle.setInfo("video", {})
            utils.addLinkItem({"mode": "nop"}, self.oHandle, liStyle)
        xbmcplugin.endOfDirectory(handle=self.oHandle, succeeded=True)

    def get_meteo_data(self, locName, nPage):
        if(nPage==0):
            url = self.meteoDataUrlDI
        else:
            url = self.meteoDataUrlDI_ND
        url = url.replace("[LOC_NAME]", locName)
        url = url.replace("[DAY_NO]", str(nPage))
        sHtml = urllib2.urlopen(url).read()
        soup = BeautifulSoup(sHtml, 'html.parser')
        mydivs =soup.find_all('div', {"class": "row-table noPad"})
        for singleDiv in mydivs:
            sHour = ""
            sTemperature=""
            sTempPerc = ""
            sUmidi=""
            sPrecipitaz=""
            mydivs =singleDiv.find('div', {"class": "col-xs-1-4"})
            if(mydivs):
                sHour = mydivs.getText().strip()
                mydivs =singleDiv.find('div', {"class": "altriDati-windchill"})
                sTempPerc =float(mydivs.select(".switchcelsius")[0].getText().strip().encode("utf-8").replace("°", ""))
                mydivs =singleDiv.find('div', {"class": "altriDati-precipitazioni"})
                sPrecipitaz = mydivs.getText().strip()
                sPrecipitaz = re.sub(r'[^0-9.]', '', sPrecipitaz)
                mydivs =singleDiv.find('div', {"class": ["col-xs-1-2","col-sm-1-5"]})
                sTemperature=float(mydivs.select(".switchcelsius")[0].getText().strip().encode("utf-8").replace("°", ""))
                mydivs=singleDiv.find('div', {"class": "altriDati-umidita"})
                sUmidi=int(mydivs.getText().strip().replace("%",""))
                mydivs=singleDiv.find('div', {"class": "col-xs-2-4"})
                sDescri = mydivs.getText().strip().encode("utf-8")
                nHour=int(sHour[:2])
                if(nHour<=23 and nHour>5):
                    nPageIdx=nPage
                else:
                    nPageIdx=nPage+1
                if(nHour in self.aMeteoMoreData[nPageIdx]):
                    self.aMeteoMoreData[nPageIdx][nHour]["d"] =sDescri
                    self.aMeteoMoreData[nPageIdx][nHour]["tp"] =sTempPerc
                    self.aMeteoMoreData[nPageIdx][nHour]["p"] =sPrecipitaz
                    self.aMeteoMoreData[nPageIdx][nHour]["t"] =sTemperature
                    self.aMeteoMoreData[nPageIdx][nHour]["u"] =sUmidi
                else:
                    self.aMeteoMoreData[nPageIdx][nHour] ={"d": sDescri, "tp":sTempPerc, "p":sPrecipitaz, "t": sTemperature, "u":sUmidi}