# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmezek.com']
        self.base_link = 'http://filmezek.com'
        self.search_link = '/search_cat.php?film=%s&type=1'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:    
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(localtitle))
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'col-md-2 col-md-offset-0 col-xs-offset-2'})

            result = [i for i in result if self.base_link + '/online-filmek/' in i]
            result = [(client.parseDOM(i, 'h5')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('(\d{4})\.', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            if not len(result) == 1: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            url = url.encode('utf-8')
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)

            items = client.parseDOM(r, 'div', attrs={'class': 'col-md-offset-1 panel panel-default'})[0]
            items = re.findall('(?s)<div class="row">\s*<.+?>\s*<h5>([^<>]+)<\/h5>.+?<h5>([^<>]+)<\/h5>.+?<h5>([^<>]+)<\/h5>.+?<a href="([^"]+)"', items)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in items:
                try: 
                    host = item[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    info = []
                    if 'magyar szinkronos' in item[1].lower(): info.append('szinkron')
                    q = item[2].lower()
                    if q == 'hd': quality = 'HD'
                    elif 'cam' in q or q == 'mozis': quality = 'CAM'
                    else: quality = 'SD'
                    url = item[3]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
            return url