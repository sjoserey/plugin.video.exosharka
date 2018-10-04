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


import re,base64,urlparse
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import dom_parser2


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cutemovie.net']
        self.base_link = 'http://cutemovie.net'
        self.search_link = 'search-movies/%s.html'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title).replace('-','+')
            url = urlparse.urljoin(self.base_link, (self.search_link % clean_title))
            r = client.request(url)
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], re.findall('onmouseover="Tip\(\'<b><i>([^<>]+)<', i)[0], re.findall('\:\s*(\d{4})\s*<', i)[0]) for i in results]

            try:
                url = [i[0] for i in results if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]
            except:
                url = None

            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            r = client.request(url)
            r = dom_parser2.parse_dom(r, 'p', {'class': 'server_play'})
            r = [dom_parser2.parse_dom(i, 'a', req=['href']) for i in r if i]
            r = [(i[0].attrs['href'], re.search('/(\w+).html', i[0].attrs['href'])) for i in r if i]
            r = [(i[0], i[1].groups()[0]) for i in r if i[0] and i[1]]

            for i in r:
                try:
                    host = i[1]
                    if str(host) in str(hostDict):
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        sources.append({
                            'source': host,
                            'quality': 'SD',
                            'language': 'en',
                            'url': i[0].replace('\/','/'),
                            'direct': False,
                            'debridonly': False
                        })
                except: pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            r = client.request(url)
            url = re.findall('document.write.+?"([^"]*)', r)[0]
            url = base64.b64decode(url)
            url = re.findall('src="([^"]*)', url)[0]
            return url
        except:
            return
