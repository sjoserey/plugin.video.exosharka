# -*- coding: utf-8 -*-

import re,urllib,urlparse,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['webmoovies.com']
        self.base_link = 'http://webmoovies.com'
        self.search_link = '/ajax/search.php'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            post = urllib.urlencode({'q': title, 'limit': '5'})
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post = post)
            result = json.loads(r)

            result = [i for i in result if 'movie' in i['meta'].lower()]
            for i in result:
                try: 
                    t = re.findall('\(([^\)]+)', i['title'])[0]
                    if t.isdigit(): t = i['title']
                except: t = i['title']
                t = t.encode('utf-8')
                if cleantitle.get(title) == cleantitle.get(t): url = i['permalink'].encode('utf-8'); break
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

            post = urllib.urlencode({'q': title, 'limit': '5'})
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post = post)
            result = json.loads(r)

            result = [i for i in result if 'tv show' in i['meta'].lower()]
            result = [i for i in result if cleantitle.get(title) in cleantitle.get(i['title'].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            urlpri = result[0]['permalink'].encode('utf-8')
            urlsec = '/season/%s/episode/%s'
            
            url = urlpri + urlsec % (season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf8')
            except: pass

            result = client.parseDOM(r, 'div', attrs={'id': 'link_list'})[0]
            result = result.split('<div class="span-16')
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]
            
            for item in result:
                try:
                    host = client.parseDOM(item, 'span')[0].strip().lower()
                    host = host.split('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if (not host in hostDict or host == 'youtube.com'): raise Exception()
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret='href')
                    url = [i for i in url if i.startswith('http')][0]
                    url = url.encode('utf-8')
                    l = re.search('images\/([a-zA-Z]+)', item).group(1).lower()
                    info = 'szinkron' if l == 'hun' else ''
                    
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = re.search('//adf.ly/[0-9]+/(.*)', url).group(1)
            if not url.startswith('http'): url = 'http://' + url
            return url
        except: 
            return
