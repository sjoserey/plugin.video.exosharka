# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['nonstopmozi.hu']
        self.base_link = 'http://nonstopmozi.hu'
        self.search_link = '/online-filmek/kereses/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:    
            t = title
            t = re.sub('(\\\|/| -|:|;|,|\.| |\*|\?|"|\'|<|>|\|)', '-', t)
            
            query = urlparse.urljoin(self.base_link, self.search_link % t)
            post = urllib.urlencode({'keres': title, 'submit': 'Keresés'})
            r = client.request(query, post=post)
            result = client.parseDOM(r, 'div', attrs={'class': 'col-md-2 w3l-movie-gride-agile'})

            result = [i for i in result if self.base_link + '/online-filmek/' in i]
            result = [(client.parseDOM(i, 'a', ret='title')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()
            
            result = [(re.search('>\((\d{4})\)<', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlr + '/linkek'
            url = url.encode('utf-8')
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)
            r = client.parseDOM(r, 'table', attrs={'class': 'linktabla'})[0]

            result = r.split('</tr>')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in result:
                try: 
                    itemreg = re.search('(?s)images\/([^\/\.]+)\..+?td align.+?>\s*(.+?)\s*<.+?images\/([^\/\.]+)\..+?href=\'([^\']+)', item)
                    host = itemreg.group(3)
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = itemreg.group(2)
                    if 'Mozis' in q: quality = 'CAM'
                    elif 'DVD' in q: quality = 'SD'  
                    elif 'HD' in q: quality = 'HD'               
                    else: quality = 'SD'
                    l = itemreg.group(1)
                    l = l.strip().lower()
                    info = 'szinkron' if l == 'magyar' else ''
                    url = itemreg.group(4)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
            return url