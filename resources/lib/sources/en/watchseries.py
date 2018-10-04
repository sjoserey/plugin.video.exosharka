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

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['watch-series.io', 'watch-series.co','watch-series.ru']
        self.base_link = 'https://watch-series.io'
        self.search_link = 'search.html?keyword=%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.query(tvshowtitle)))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            result = client.request(url)
            dom_s = client.parseDOM(result, 'li', attrs={'class': 'video-block'})
            dom_s = client.parseDOM(dom_s, 'a', ret='href')
            express = '-season-0*?%s-?' % season
            get_season = [i for i in dom_s if re.search(express, i)][0]
            url = urlparse.urljoin(self.base_link, get_season + '/season')
            result = client.request(url)
            dom_e = client.parseDOM(result, 'div', attrs={'class': 'video_container'})
            dom_e = client.parseDOM(dom_e, 'a', ret='href')
            express = '-episode-0*?%s-?' % episode
            get_ep = [i for i in dom_e if re.search(express, i)][0]
            get_ep = urlparse.urljoin(self.base_link, get_ep)
            url = get_ep.encode('utf-8')
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
        
            hostDict += ['akamaized.net', 'google.com', 'picasa.com', 'blogspot.com']
            result = client.request(url)
            
            dom = dom_parser.parse_dom(result, 'a', req='data-video')
            urls = [i.attrs['data-video'] if i.attrs['data-video'].startswith('http') else 'http:' + i.attrs['data-video'] for i in dom]

            for url in urls:
                try:
                    dom = []
                    if 'vidnode.net/streaming' in url:
                        result = client.request(url, timeout='10')

                        src = re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([\d]+)''', result, re.DOTALL)
                        src = [i for i in src if 'play?fileName' in i[0]]

                        links = [(i[0], '1080p') for i in src if int(i[1]) >= 1080]
                        links += [(i[0], 'HD') for i in src if 720 <= int(i[1]) < 1080]
                        links += [(i[0], 'SD') for i in src if int(i[1]) < 720]
                        for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'language': 'en', 'url': i[0], 'direct': True, 'debridonly': False})
                    elif 'ocloud.stream' in url:
                        result = client.request(url, timeout=10)
                        base = re.findall('<base href="([^"]+)">', result)[0]
                        hostDict += [base]
                        dom = dom_parser.parse_dom(result, 'a', req=['href','id'])
                        dom = [(i.attrs['href'].replace('./embed',base+'embed'), i.attrs['id']) for i in dom if i]
                        dom = [(re.findall("var\s*ifleID\s*=\s*'([^']+)", client.request(i[0]))[0], i[1]) for i in dom if i]                        
                    if dom:                
                        try:
                            for r in dom:
                                valid, hoster = source_utils.is_host_valid(r[0], hostDict)
    
                                if not valid: continue
                                quality = source_utils.label_to_quality(r[1])
                                urls, host, direct = source_utils.check_directstreams(r[0], hoster)
                                for x in urls:
                                    if direct: size = source_utils.get_size(x['url'])
                                    if size: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False, 'info': size})         
                                    else: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})         
                        except: pass
                    else:
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        if not valid: continue
                        try:
                            url.decode('utf-8')
                            sources.append({'source': hoster, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                        except:
                            pass
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        if 'vidcdn.pro' in url: url = url.replace('https', 'http')
        if 'play?fileName' in url:
            r = client.request(url, output='extended', redirect=False)
            location = r[2]['Location']
            url = urlparse.urljoin(url, location)
        return url
