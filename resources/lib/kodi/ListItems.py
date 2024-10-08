import sys

import xbmcgui
from future.standard_library import install_aliases

install_aliases()
from urllib.parse import urlencode


class ListItems:

    def __init__(self, addon):
        self.addon = addon
        quality = self.addon.getSetting('image_quality')
        self.quality = int(quality) if quality else 1

    def _band_quality(self):
        if self.quality == 0:
            return 1 # full resolution
        if self.quality == 1:
            return 10 # 1200px wide
        if self.quality == 2:
            return 25 # 700px wide

    def _album_quality(self):
        if self.quality == 0:
            return 5 # 700px wide
        if self.quality == 1:
            return 2 # 350px wide
        if self.quality == 2:
            return 9 # 210px wide

    def _build_url(self, query):
        base_url = sys.argv[0]
        return base_url + '?' + urlencode(query)

    def get_root_items(self, username):
        items = []
        # discover menu
        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30101))
        li.setArt({'icon': 'DefaultMusicSources.png'})
        url = self._build_url({'mode': 'list_discover'})
        items.append((url, li, True))
        # collection menu
        # don't add if not configured
        if username == "":
            li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30104))
            li.setArt({'icon': 'DefaultAddonService.png'})
            url = self._build_url({'mode': 'settings'})
            items.append((url, li, True))
        else:
            li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30102))
            li.setArt({'icon': 'DefaultMusicAlbums.png'})
            url = self._build_url({'mode': 'list_collection'})
            items.append((url, li, True))

            li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30105))
            li.setArt({'icon': 'DefaultMusicRecentlyAdded.png'})
            url = self._build_url({'mode': 'list_wishlist'})
            items.append((url, li, True))
        # search
        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30103))
        li.setArt({'icon': 'DefaultMusicSearch.png'})
        url = self._build_url({'mode': 'search', 'action': 'new'})
        items.append((url, li, True))
        return items

    def get_album_items(self, albums, band=None, group_by_artist=False):
        items = []
        if group_by_artist:
            li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30106))
            li.setArt({'icon': 'DefaultMusicArtists.png'})
            url = self._build_url({'mode': group_by_artist + '_band'})
            items.append((url, li, True))
        for album in albums:
            if band:
                album_title = '{} - {}'.format(band.band_name, album.album_name)
            elif album.band:
                album_title = '{} - {}'.format(album.band.band_name, album.album_name)
            else:
                album_title = album.album_name

            li = xbmcgui.ListItem(label=album_title)
            url = self._build_url({'mode': 'list_songs', 'album_id': album.album_id, 'item_type': album.item_type})
            band_art = band.get_art_img(quality=self._band_quality()) if band else None
            album_art = album.get_art_img(quality=self._album_quality())
            li.setArt({'thumb': album_art, 'fanart': band_art if band_art else album_art})
            items.append((url, li, True))
        return items

    def get_genre_items(self, genres):
        items = []
        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30201))
        url = self._build_url({'mode': 'list_subgenre_songs', 'category': 'all', 'subcategory': 'all'})
        items.append((url, li, True))
        for genre in genres:
            li = xbmcgui.ListItem(label=genre['name'])
            url = self._build_url({'mode': 'list_subgenre', 'category': genre['value']})
            items.append((url, li, True))
        return items

    def get_subgenre_items(self, genre, subgenres):
        items = []
        li = xbmcgui.ListItem(label=self.addon.getLocalizedString(30201) + " " + genre)
        url = self._build_url({'mode': 'list_subgenre_songs', 'category': genre, 'subcategory': 'all'})
        items.append((url, li, True))
        for subgenre in subgenres[genre]:
            li = xbmcgui.ListItem(label=subgenre['name'])
            url = self._build_url({'mode': 'list_subgenre_songs', 'category': genre, 'subcategory': subgenre['value']})
            items.append((url, li, True))
        return items

    def get_track_items(self, band, album, tracks, to_album=False):
        items = []
        for track in tracks:
            title = u"{band} - {track}".format(band=band.band_name, track=track.track_name)
            li = xbmcgui.ListItem(label=title)
            li.setInfo('music', {'duration': int(track.duration), 'album': album.album_name, 'genre': album.genre,
                                 'mediatype': 'song', 'tracknumber': track.number, 'title': track.track_name,
                                 'artist': band.band_name})
            band_art = band.get_art_img(quality=self._band_quality())
            album_art = album.get_art_img(quality=self._album_quality())
            li.setArt({'thumb': album_art, 'fanart': band_art if band_art else album_art})
            li.setProperty('IsPlayable', 'true')
            url = self._build_url({'mode': 'stream', 'url': track.file, 'title': title})
            li.setPath(url)
            if to_album:
                album_url = self._build_url(
                    {'mode': 'list_songs', 'album_id': album.album_id, 'item_type': album.item_type})
                cmd = 'Container.Update({album_url})'.format(album_url=album_url)
                commands = [(self.addon.getLocalizedString(30202), cmd)]
                li.addContextMenuItems(commands)
            items.append((url, li, False))
        return items

    def get_band_items(self, bands, from_wishlist=False, from_search=False):
        items = []
        mode = 'list_albums'
        if from_wishlist:
            mode = 'list_wishlist_band_albums'
        elif from_search:
            mode = 'list_search_albums'
        for band in bands:
            li = xbmcgui.ListItem(label=band.band_name)
            band_art = band.get_art_img(quality=self._band_quality())
            if band_art:
                li.setArt({'thumb': band_art, 'fanart': band_art})
            url = self._build_url({'mode': mode, 'band_id': band.band_id})
            items.append((url, li, True))
        return items
