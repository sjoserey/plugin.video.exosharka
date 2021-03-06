# -*- coding: utf-8 -*-

'''
    ExoShark Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,urllib,urlparse
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import cfscrape
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['filepursuit.com']
        self.base_link = 'https://filepursuit.com'
        self.search_link = '/search4/%s/type/video'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = cleantitle.getsearch(query)
            query = query.replace(' ', '+')

            url = self.search_link % query
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content
            items = client.parseDOM(r, 'table', attrs={'data-role': 'table'})[0]
            items = client.parseDOM(items, 'tr')

            for item in items:
                try:
                    url = client.parseDOM(item, 'button', ret='data-clipboard-text')[0]
                    url = url.replace(' ', '%20')
                    if not url.startswith('http'): continue
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    host = urlparse.urlparse(url.strip().lower()).netloc
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    quality, info = source_utils.get_release_quality(url)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
      return url
