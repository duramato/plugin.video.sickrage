import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import sickbeard
import urllib
import settings
from metahandler import metahandlers


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Translates the int returned from SickRage to a weekday string
def GetWeekDay(weekday):
    if weekday == 1:
        day = "[COLOR lightcyan]Monday[/COLOR]"
    elif weekday == 2:
        day = "[COLOR lightcyan]Tuesday[/COLOR]"
    elif weekday == 3:
        day = "[COLOR lightcyan]Wednesday[/COLOR]"
    elif weekday == 4:
        day = "[COLOR lightcyan]Thursday[/COLOR]"
    elif weekday == 5:
        day = "[COLOR lightcyan]Friday[/COLOR]"
    elif weekday == 6:
        day = "[COLOR lightcyan]Saturday[/COLOR]"
    elif weekday == 7:
        day = "[COLOR lightcyan]Sunday[/COLOR]"
    else:
        day = "None"
    return day


# Get upcoming episodes.
def GetUpcomingEpisodes(ext_upcoming=False):
    coming_soon = Sickbeard.GetFutureShows()
    upcoming_episodes_list = []
    
    # Get todays upcoming eps.
    if len(coming_soon["today"]) != 0:
      day = "[COLOR lightgreen]Today[/COLOR]"
      for show in coming_soon['today']:
          if show['paused'] == 0:
              paused = "Pause"
              ispaused = ""
          else:
              paused = "Resume"
              ispaused = "    [COLOR cyan]Paused[/COLOR]"
          upcoming_episodes_list.append([str(show['tvdbid']), day+": [COLOR gold]"+show['show_name']+"[/COLOR] - "+str(show['season'])+"x"+str(show['episode'])+" "+show['ep_name']+ispaused, show['show_name'], paused, show['season'], show['episode']])
          
    # Get coming soon eps.
    if len(coming_soon["soon"]) != 0:    
      show_list={}
      for show in coming_soon['soon']:
          if show['airdate'] not in show_list:
              show_list[show['airdate']] = []
              show_list[show['airdate']].append(show)
          else:
              show_list[show['airdate']].append(show)

      for k in sorted(show_list.iterkeys()):
          day = GetWeekDay(show_list[k][0]['weekday'])
          for show in show_list[k]: 
              if show['paused'] == 0:
                  paused = "Pause"
                  ispaused = ""
              else:
                  paused = "Resume"
                  ispaused = "    [COLOR cyan]Paused[/COLOR]"
              upcoming_episodes_list.append([str(show['tvdbid']), day+": [COLOR gold]"+show['show_name']+"[/COLOR] - "+str(show['season'])+"x"+str(show['episode'])+" "+show['ep_name']+ispaused, show['show_name'], paused, show['season'], show['episode']])

    # Get upcoming later eps.
    if ext_upcoming:
        if len(coming_soon["later"]) != 0:    
          show_list={}
          for show in coming_soon['later']:
              if show['airdate'] not in show_list:
                  show_list[show['airdate']] = []
                  show_list[show['airdate']].append(show)
              else:
                  show_list[show['airdate']].append(show)
    
          for k in sorted(show_list.iterkeys()):
              for show in show_list[k]: 
                  if show['paused'] == 0:
                      paused = "Pause"
                      ispaused = ""
                  else:
                      paused = "Resume"
                      ispaused = "    [COLOR cyan]Paused[/COLOR]"
                  upcoming_episodes_list.append([str(show['tvdbid']), show['airdate']+": [COLOR gold]"+show['show_name']+"[/COLOR] - "+str(show['season'])+"x"+str(show['episode'])+" "+show['ep_name']+ispaused, show['show_name'], paused, show['season'], show['episode']])

    return upcoming_episodes_list


def menu(ext_upcoming=False):
    upcoming_episodes_list = GetUpcomingEpisodes(ext_upcoming)
    upcoming_total = len(upcoming_episodes_list)
    for tvdbid, ep_name, show_name, paused, season, episode in upcoming_episodes_list:
        episode_status_args = ", "+tvdbid+", "+str(season)+", "+str(episode)
        
        context_menu_items = []
        context_menu_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_menu_items.append(('ExtendedInfo', 'XBMC.RunPlugin(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=10&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Episode List', 'XBMC.Container.Update(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=4&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Set Episode Status', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setstatus.py'+episode_status_args+')'))
        context_menu_items.append(('Add New Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/addshow.py, new)'))
        context_menu_items.append(('Delete Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/deleteshow.py, '+tvdbid+', '+show_name+')'))
        context_menu_items.append(('Force Update', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/forcesearch.py, '+tvdbid+')'))
        context_menu_items.append((paused+' Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setpausestate.py, '+paused+', '+tvdbid+')'))
        if xbmc.getCondVisibility('System.HasAddon(context.videolookup.dialog)'):
            context_menu_items.append(('Video Lookup', 'XBMC.RunScript(context.videolookup.dialog)'))
        else:
            context_menu_items.append(('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'))
        context_menu_items.append(('Go Back', 'XBMC.Action(back)'))
        
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        addShowDirectory(show_name, ep_name, tvdbid, season, episode, 6, thumbnail_path, fanart_path, upcoming_total, context_menu_items)

    xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')


def addShowDirectory(show_name, ep_name, tvdbid, season, episode, menu_number, thumbnail_path, fanart_path, show_total, context_menu_items):
    url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode="+str(menu_number)+"&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(ep_name, thumbnailImage=thumbnail_path)
    list_item.setProperty('fanart_image', fanart_path) 
    list_item.setProperty('LibraryHasMovie', '0')  # Removes the "Play" button from the video info screen, and replaces it with "Browse".
    meta = {}
    metaget = metahandlers.MetaData()
    try:
        meta = metaget.get_episode_meta(show_name, tvdbid, int(season), int(episode), '', '', '')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_menu_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False, totalItems=show_total)  

