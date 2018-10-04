# -*- coding: utf-8 -*-

import re,urllib,urlparse,HTMLParser

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import es_utils
from resources.lib.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['moziclub.eu']
        self.base_link = 'https://www.moziclub.eu'
        self.search_link = '/?s=%s+%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote_plus(title), year))
            r = client.request(query, timeout=10)
            r = HTMLParser.HTMLParser().unescape(r)

            result = client.parseDOM(r, 'div', attrs={'class': 'post-container'})

            result = [(re.findall('bookmark">\s*([^<>].+?)\s*\(\d{4}\)\s*<\/a', i)[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = client.request(url)

            result = client.parseDOM(r, 'table', attrs={'id': 'forrlist'})

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = client.parseDOM(item, 'td')[1]
                    if '<img' in host:
                        itemreg = re.search('(?s)img.+?src="([^"]+)".+?><img.+?src="([^"]+)".+?img.+?src="([^"]+)".+?href="([^"]+)', item)
                        host = itemreg.group(3)
                        url = itemreg.group(4)
                    else:
                        itemreg = re.search('(?s)img.+?src="([^"]+)".+?><img.+?src="([^"]+)".+?href="([^"]+)', item)
                        host = host
                        url = itemreg.group(3)
                    hostc = host.rsplit('/', 1)[-1].split('.', 1)[0].split('(', 1)[0].split('-', 1)[0].strip().lower()
                    # host correction >>
                    if 'indavideo' in hostc: host = 'indavideo'
                    elif 'vidtome' in hostc: host = 'vidto'
                    elif '1fichier' in hostc: host = '1fichier'
                    elif 'vidlox' in hostc: host = 'vidlox'
                    elif 'thevideo' in hostc: host = 'thevideo'
                    else: host = hostc
                    # << host correction
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = itemreg.group(2)
                    q = q.rsplit('/', 1)[-1].split('.', 1)[0]
                    if q == '5': quality = 'HD'
                    else: quality = 'SD'
                    l = itemreg.group(1)
                    l = l.rsplit('/', 1)[-1].split('.', 1)[0]
                    info = 'szinkron' if l == '3' else ''
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            scraper = cfscrape.create_scraper()
            r = scraper.get(url).content
            ysmm = re.findall('var ysmm = \'(.*?)\';', r)[0]
            url = es_utils.adfly_crack(ysmm)
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
