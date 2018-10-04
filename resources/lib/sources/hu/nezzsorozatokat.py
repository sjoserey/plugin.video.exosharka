# -*- coding: utf-8 -*-

import re,urllib,urlparse,json
from resources.lib.modules import client
from resources.lib.modules import cleantitle

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['nezzsorozatokat.info']
        self.base_link = 'http://nezzsorozatokat.info'
        self.search_link = '/js/autocomplete_ajax.php?term=%s'

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
            episode = episode.zfill(2)
            season = season.zfill(2)
            
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(title))
            r = client.request(query)
            result = json.loads(r)

            result = [i for i in result if cleantitle.get(title) in cleantitle.get(i['label'].encode('utf-8'))]
            result = [i for i in result if 'S%sE%s' % (season, episode) in i['label']]
            if len(result) == 0: raise Exception()
            
            url = urlparse.urljoin(self.base_link, '/?' + result[0]['id'])
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            
            if url == None: return sources
            
            r = client.request(url)
            
            result = client.parseDOM(r, 'div', attrs={'id': 'main'})
            result = result[0].split('<p class')
            if len(result) == 0: raise Exception() 

            for item in result:
                try:
                    try: id = client.parseDOM(item, 'div', ret='load-id')[0]
                    except: id = client.parseDOM(item, 'div', ret='sorsz')[0]
                    query = urlparse.urljoin(self.base_link, '/videobetolt.php?id=' + id)
                    r = client.request(query, timeout='10')
                    try: url = client.parseDOM(r, 'iframe', ret='src')[0]
                    except: url = client.parseDOM(r, 'IFRAME', ret='SRC')[0]
                    url = url.encode('utf-8')
                    host = urlparse.urlparse(url.strip().lower()).netloc
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(item, 'span', attrs={'class': 'doboz'})[0]
                    info = 'szinkron' if 'magyar szinkron' in l.lower() else ''
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url
