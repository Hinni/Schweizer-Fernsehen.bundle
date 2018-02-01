# -*- coding: utf-8 -*-

PREFIX = '/video/schweizerfernsehen'
NAME = L('Title')
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

API_BASE = 'https://www.srf.ch'
API_INIT = API_BASE + '/podcasts'
API_SHOW = API_BASE + '/feed/podcast/hd/%s.xml'

####################################################################################################
# Initialize plugin
def Start():

    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR

    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)


####################################################################################################
# Our main menu is static
@handler(PREFIX, NAME, art=ART, thumb=ICON)
def VideoMainMenu():

    oc = ObjectContainer(title1=L('Title'))

    oc.add(DirectoryObject(key=Callback(SubMenu, title=L('Alle TV-Sendungen'), url='pt-tv'), title=L('Alle TV-Sendungen')))
    oc.add(DirectoryObject(key=Callback(SubMenu, title='SRF 1', url='pr-srf-1'), title='SRF 1'))
    oc.add(DirectoryObject(key=Callback(SubMenu, title='SRF zwei', url='pr-srf-2'), title='SRF zwei'))
    oc.add(DirectoryObject(key=Callback(SubMenu, title='SRF info', url='pr-srf-info'), title='SRF info'))

    return oc


####################################################################################################
# List shows of the selected channel
@route(PREFIX + '/submenu')
def SubMenu(title, url):

    oc = ObjectContainer(title1=L('Title'), title2=title)

    # Load data for given channel
    try:
        source = HTML.ElementFromURL(API_INIT)
    except Exception as e:
        Log.Error(e)
        return ObjectContainer(header=L('Empty'), message=L('There are no shows available.'))

    # Filter all available shows with given channel
    shows = source.xpath('//li[contains(@data-filter-options,"' + url + '")]')

    # Loop over filtered results
    for show in shows:

        show_title = show.xpath('./a/img')[0].get('title')
        show_summary = show.xpath('./div[@class="module-content"]/p')[0].text
        show_thumb = show.xpath('./a/img')[0].get('data-original-src') # in most cases a better choice than data-retina-src
        show_id = show.xpath('.//div[contains(@class, "podcast-data")]')[0].get('data-podcast-uuid') # we need the guid from the url

        # Check if thumb is a complete url
        if (show_thumb.startswith('http') != True) : show_thumb = API_BASE + show_thumb

        oc.add(TVShowObject(
            key=Callback(GetDirectory, title=show_title, id=show_id),
            rating_key=show_id,
            title=show_title,
            summary=show_summary,
            thumb=Resource.ContentsOfURLWithFallback(show_thumb))
        )

    return oc


####################################################################################################
# List episodes of the selected show
@route(PREFIX + '/directory')
def GetDirectory(title, id):

    oc = ObjectContainer(title1=L('Title'), title2=title)

    url = API_SHOW %id
    try:
        feed = XML.ObjectFromURL(url, cacheTime=None)
    except Exception as e:
        Log.Error(e)
        return ObjectContainer(header=L('Empty'), message=L('There are no episodes available.'))

    for item in feed['item']:

        try:
            item_id = item['guid'][0]
        except:
            pass

        url = API_SHOW %item_id

        oc.add(VideoClipObject(
            url = url,
            title = item['title'],
            summary = item['itunes:subtitle'],
            thumb = Resource.ContentsOfURLWithFallback(item['itunes:image'])
        ))

    return oc
