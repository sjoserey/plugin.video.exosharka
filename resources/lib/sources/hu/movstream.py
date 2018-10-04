# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['movstream.do.am']
        self.base_link = 'http://movstream.do.am'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:    
            query = urlparse.urljoin(self.base_link, '/load/')
            post = urllib.urlencode({'query': localtitle, 'a': '2'})
            r = client.request(query, post=post)
            result = client.parseDOM(r, 'div', attrs={'class': 'poster_box'})

            result = [i for i in result if not '/load/sorozatok/' in i]
            result = [(client.parseDOM(i, 'div', ret='title')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()
            
            result = [(re.search('block-subtitle">\s*(\d{4})\s*<', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr)
            url = url.encode('utf-8')
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)

            tag = client.parseDOM(r, 'div', attrs={'class': 'vep-details'})[0]
            tag = tag.lower()

            q = re.search('vep-author[->]+\s*(.+?)\s*<\/span', tag).group(1)
            if 'cam' in q or 'mozis' in q: quality = 'CAM'
            else: quality = 'SD'
            l = re.search('vep-channel[->]+\s*(.+?)\s*<\/span', tag).group(1)
            info = []
            if not 'felirat' in l and not 'angol' in l: info.append('szinkron')

            result = client.parseDOM(r, 'div', attrs={'class': 'vep-year'})[0]
            items = re.findall('href="([^"]+)"[^>]+>([^<>]+)<\/a', result)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in items:
                try: 
                    host = item[1]
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item[0]
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