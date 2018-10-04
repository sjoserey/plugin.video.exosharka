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

import re, urllib, urlparse

from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['full4movies.co']
        self.base_link = 'https://www.full4movies.co'
        self.search_link = '/advanced-search/?%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urllib.urlencode({'search_query': title, 'orderby': '', 'order': '', 'tax_release-year[]': year, 'wpas': '1'})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            result = self.scraper.get(query).content

            result = client.parseDOM(result, 'div', attrs={'class': 'datos'})
            if len(result) == 0: raise Exception()

            result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].split('(English', 1)[0].encode('utf-8')) and not 'Hindi' in i[0]]
            if len(result) == 0: raise Exception()

            return result[0]
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            r = self.scraper.get(url).content

            tag = client.parseDOM(r, 'span', attrs={'class': 'calidad2'})[0]
            tag = tag.lower()
            if 'cam' in tag: quality = 'CAM'
            elif '1080p' in tag: quality = '1080p'
            elif '720p' in tag: quality = '720p'
            else: quality = 'SD'

            items = re.findall('<a class="myButton" href="([^"]+)"', r)

            for item in items:
                try:
                    valid, hoster = source_utils.is_host_valid(item, hostprDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})
                    valid, hoster = source_utils.is_host_valid(item, hostDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
