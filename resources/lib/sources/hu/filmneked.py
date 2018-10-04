# -*- coding: utf-8 -*-

import re,urllib,urlparse,json

from resources.lib.modules import client
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmneked.com']
        self.base_link = 'http://filmneked.com'
        self.search_link = '/typeahead/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(title))
            r = client.request(query, XHR=True)
            result = json.loads(r)

            result = [i for i in result if i['background'].rsplit('/', 1)[-1].split('.')[0] == imdb]
            if not result: raise Exception()
            url = result[0]['link'].encode('utf-8')
			
			
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return            
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(title))
            r = client.request(query, XHR=True)
            result = json.loads(r)

            result = [i for i in result if i['background'].rsplit('/', 1)[-1].split('.')[0] == imdb]
            if not result: raise Exception()

            urlpri = result[0]['link'].encode('utf-8')
            urlsec = '/seasons/%s/episodes/%s'

            url = urlpri + urlsec % (season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            
            r = client.request(url)
            result = client.parseDOM(r, 'center')
            url = client.parseDOM(result, 'a', ret='href')[0]
			
            r = client.request(url)
            result = client.parseDOM(r, 'tr', attrs={'data-id': '\d+'})
            
            for i in result:
                try:
                    url = client.parseDOM(i, 'td', ret='data-bind')[0]
                    url = re.search('["\'](https?://[^"\']+)', url).group(1)
                    url = url.encode('utf-8')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    info = 'szinkron' if ('lang o1hun' in i or 'lang o2hun' in i) else ''
                    if 'quality HD' in i or 'quality BDRIP' in i: quality = 'HD'
                    elif 'quality M' in i or 'quality CAM' in i: quality = 'CAM'
                    else: quality = 'SD'
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url
