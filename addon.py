# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import resources.lib.utils as utils
from resources.lib.manageData import ManageData
from resources.lib.locSearch import LocSearch

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
#import web_pdb
    
# plugin constants
__plugin__ = "plugin.image.sdf3BMeteo"
__author__ = "fabpolli"
 
addon = xbmcaddon.Addon(id=__plugin__)
__profile__ = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
if(not os.path.isdir(__profile__)):
    os.makedirs(__profile__)

# plugin handle
handle = int(sys.argv[1])
addonname = addon.getAddonInfo('name')
params = utils.parameters_string_to_dict(sys.argv[2])
mode = str(params.get("mode", ""))
clearImageCacheFlag=addon.getSetting("clearImageCache")
starred1 = addon.getSetting("Starred1")
starred2 = addon.getSetting("Starred2")
starred3 = addon.getSetting("Starred3")
starred4 = addon.getSetting("Starred4")
starred5 = addon.getSetting("Starred5")


def set_new_pref():
    name_loc = str(params.get("name_loc", ""))
    id_localita = str(params.get("id_localita", ""))
    sToSet = name_loc + "#"+id_localita
    starred1 = addon.getSetting("Starred1")
    starred2 = addon.getSetting("Starred2")
    starred3 = addon.getSetting("Starred3")
    starred4 = addon.getSetting("Starred4")
    starred5 = addon.getSetting("Starred5")
    if(starred1==""):
        addon.setSetting("Starred1", sToSet)
        starred1 = sToSet
    elif(starred2==""):
        addon.setSetting("Starred2", sToSet)
        starred2 = sToSet
    elif(starred3==""):
        addon.setSetting("Starred3", sToSet)
        starred3 = sToSet
    elif(starred4==""):
        addon.setSetting("Starred4", sToSet)
        starred4 = sToSet
    else:
        addon.setSetting("Starred5", sToSet)
        starred5 = sToSet
    xbmc.executebuiltin('Notification(%s, %s, %d)'%(addonname,"Località aggiunta ai preferiti", 2000))
    xbmc.executebuiltin('Action(%s)'%("Back"))
    

def manage_new_pref():
    sLocToFind = utils.get_user_input('Indica il nome della località da aggiungere ai preferiti')
    if(sLocToFind):
        oLocSearch = LocSearch(__profile__, handle, addonname)
        oLocSearch.doSearch(sLocToFind)

def show_config_menu():
    liStyle = xbmcgui.ListItem("Aggiungi località preferita")
    utils.addDirectoryItem({"mode": "addpref"}, handle, liStyle)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def showDayData():
    locCode = int(str(params.get("locCode", "")))
    locName = str(params.get("locName", ""))
    dataManager = ManageData(__profile__, handle)
    dataManager.show_day_forecast(mode, locCode, locName)

def addItemRootMenu(sText, sCode):
    liStyle = xbmcgui.ListItem(sText)
    utils.addDirectoryItem({"mode": "showloc", "locCode": sCode, "locName": sText}, handle, liStyle)
    
def show_root_menu():
    numStarred = 0
    if(not starred1==""):
        numStarred += 1
        aData = starred1.split('#')
        addItemRootMenu(aData[0], aData[1])
    if(not starred2==""):
        numStarred += 1
        aData = starred2.split('#')
        addItemRootMenu(aData[0], aData[1])
    if(not starred3==""):
        numStarred += 1
        aData = starred3.split('#')
        addItemRootMenu(aData[0], aData[1])
    if(not starred4==""):
        numStarred += 1
        aData = starred4.split('#')
        addItemRootMenu(aData[0], aData[1])
    if(not starred5==""):
        numStarred += 1
        aData = starred5.split('#')
        addItemRootMenu(aData[0], aData[1])
    if(numStarred<5):
        show_config_menu()
    else:
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
def show_days_menu():
    #web_pdb.set_trace()
    today = datetime.date.today();
    attDow = today.weekday();
    locCode = str(params.get("locCode", ""))
    locName = params.get("locName", "")
    for day_idx in range(7):
        attDate = today + datetime.timedelta(days=day_idx)
        if(day_idx==0):            
            liStyle = xbmcgui.ListItem("Oggi")
        else:
            if(day_idx==1):
                liStyle = xbmcgui.ListItem("Domani")
            else:
                liStyle = xbmcgui.ListItem(utils.dowArray[day_idx] + " " + attDate.strftime("%d") + " " + utils.monthArray[int(attDate.strftime("%m"))])
        utils.addDirectoryItem({"mode": "page-"+str(day_idx), "locCode": locCode, "locName": locName}, handle, liStyle)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def clearImageCache():
    folder = __profile__
    for the_file in os.listdir(folder):
        if(the_file<>"settings.xml"):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                pass
    addon.setSetting("clearImageCache", "false")

if(clearImageCacheFlag=='true'):
    clearImageCache()

#xbmc.log(str(sys.version_info[0]),xbmc.LOGNOTICE)
if mode[:4]=="page":
    showDayData()
elif mode=="nop":
    pass
elif mode=="addpref":
    manage_new_pref()
elif mode=="setPref":
    set_new_pref()
elif mode=="showloc":
    show_days_menu()
else:
    show_root_menu()