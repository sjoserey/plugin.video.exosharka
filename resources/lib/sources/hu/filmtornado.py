# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmtornado.cc']
        self.base_link = 'https://filmtornado.cc'
        self.search_link = '/search.php'
        self.host_link = 'https://onlinefilmekneked.ru'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            post = {'search': title}
            post = urllib.urlencode(post)
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post=post)
            
            r = r.split('</h3>')
            r = [client.parseDOM(i, 'a', ret='href')[0] for i in r if 'h3>' + localtitle in i]

            for i in r:
                url = client.replaceHTMLCodes(i)
                url = url.encode('utf-8')
                src = client.request(url)
                yr = re.search('<h1>[^<>]+\(\s*(\d{4})\s*\)', src).group(1)
                if not yr == year: raise Exception()
                titl = client.parseDOM(src, 'div', attrs = {'class': 'col-lg-3 col-md-4 col-sm-8 col-xs-12'})[0]
                if cleantitle.get(re.findall('Eredeti.+?h2>(.+?)<', titl)[0]) == cleantitle.get(title):
                    urlr = url.rsplit('/', 1)[-1]
                    query = urlparse.urljoin(self.host_link, '/Online-filmek-neked/Film/' + urlr)
                    r = client.request(query)
                    url = client.parseDOM(r, 'table', attrs = {'class': 'table table-hover'})
                    return (url[0], '')
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

            post = {'search': title}
            post = urllib.urlencode(post)
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query, post=post)

            r = r.split('</h3>')
            r = [client.parseDOM(i, 'a', ret='href')[0] for i in r if '-%s-evad' % season in i]

            for i in r:
                url = client.replaceHTMLCodes(i)
                url = url.encode('utf-8')
                src = client.request(url)
                titl = client.parseDOM(src, 'div', attrs = {'class': 'col-lg-3 col-md-4 col-sm-8 col-xs-12'})[0]
                if cleantitle.get(re.findall('Eredeti.+?h2>(.+?)<', titl)[0]) == cleantitle.get(title):
                    urlr = url.rsplit('/', 1)[-1]
                    query = urlparse.urljoin(self.host_link, '/Online-filmek-neked/Film/' + urlr)
                    r = client.request(query)
                    url = client.parseDOM(r, 'table', attrs = {'class': 'table table-hover'})
                    return (url[0], episode)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            result = url[0].split('</tr>')
            result = [i for i in result if '/Online-filmek-neked/Online/' in i]

            if url[1].isdigit():
                result = [i for i in result if '>%s. epiz' % url[1] in i]

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    itemreg = re.search('data-href="?\'?([^"\'>]*).+?src.+?img\/(\d{1}).+?<div>(.+?)<.+?td><div>(.+?)<', item)
                    host = itemreg.group(4)
                    host = host.split()[0].rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = itemreg.group(3)
                    if q == 'DVD' or q == 'TV': quality = 'SD'
                    elif q == 'HD': quality = 'HD'
                    elif q == 'CAM': quality = 'CAM'
                    else: quality = 'SD'
                    info = []
                    l = itemreg.group(2)
                    if l == '3': info.append('szinkron')
                    url = itemreg.group(1)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            if '/http' in url:
                url = url.rsplit('/http', 1)[1]
                url = 'http' + url
            r = client.request(url)
            try: url = client.parseDOM(r, 'iframe', ret='src')[-1]
            except: url = client.parseDOM(r, 'IFRAME', ret='SRC')[-1]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
