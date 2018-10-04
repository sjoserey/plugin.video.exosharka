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


import re, urlparse, urllib, json

from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser2
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movie4u.ch', 'movie4u.live']
        self.base_link = 'https://movie4u.live'
        self.search_link = '/?s=%s'
        self.tv_search_link = '/wp-json/dooplay/search/?keyword=%s&nonce=b25f8f344b'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = self.scraper.get(search_url).content
            r = client.parseDOM(r, 'div', {'class': 'result-item'})
            r = [(dom_parser2.parse_dom(i, 'a', req='href')[0],
                  re.sub('<.*?>', '' , re.findall('alt=\"(.*?)\"', i)[0]),
                  dom_parser2.parse_dom(i, 'span', attrs={'class': 'year'})) for i in r]

            r = [(i[0].attrs['href'], i[1], i[2][0].content) for i in r if
                 (cleantitle.get(i[1]) == cleantitle.get(title) and i[2][0].content == year)]
            url = r[0][0]
    
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(tvshowtitle)
            search_url = urlparse.urljoin(self.base_link, self.tv_search_link % clean_title.replace('-', '+'))
            r = self.scraper.get(search_url).content
            r = json.loads(r)
            url = [(r[i]['url']) for i in r if
                 (cleantitle.get(r[i]['title']) == cleantitle.get(tvshowtitle))]
            url = source_utils.strip_domain(url[0])

            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            t = url.split('/')[2]
            url = self.base_link + '/episodes/%s-%dx%d' % (t, int(season), int(episode))
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = self.scraper.get(url).content
            data = client.parseDOM(r, 'div', attrs={'class': 'playex'})
            data = [client.parseDOM(i, 'a', ret='href') for i in data if i]
            r = self.scraper.get(data[0][0]).content
            data = client.parseDOM(r, 'div', attrs={'class': 'playex'})
            data = [client.parseDOM(i, 'iframe', ret='src') for i in data if i]

            for url in data[0]:
                try:
                    link = self.scraper.get(url).url
                    valid, host = source_utils.is_host_valid(link, hostDict)
                    quality, info = source_utils.get_release_quality(link, None)
                    if not valid: continue
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': quality,
                        'language': 'en',
                        'url': link.replace('\/', '/'),
                        'direct': False,
                        'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
