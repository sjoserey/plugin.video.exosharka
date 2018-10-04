# -*- coding: utf-8 -*-

import re,urllib,urlparse

from resources.lib.modules import client
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filminvazio.com']
        self.base_link = 'http://filminvazio.com'
        self.search_link = '/filmkereso/?%s'
        self.host_link = 'http://ncoredb.com/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urllib.urlencode({'search_query': localtitle, 'orderby': '', 'order': '', 'tax_fecha-estreno[]': year, 'wpas': '1'})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            result = client.request(query)

            result = client.parseDOM(result, 'div', attrs={'class': 'datos'})
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            
            if not result: raise Exception()
                
            r = client.request(result[0])
            result = client.parseDOM(r, 'div', attrs={'class': 'enlaces_box'})
            url = client.parseDOM(result, 'a', ret = 'href')[0]
            return url
            
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            
            r = client.request(url)
            #result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(r, 'div', attrs={'class': 'enlaces_box'})
            result = client.parseDOM(result, 'li', attrs={'class': 'elemento'})
            for item in result:
                try:
                    host = client.parseDOM(item, 'img', ret = 'alt')[0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = client.parseDOM(item, 'a', ret = 'href')[0]
                    url = url.encode('utf-8')
                    q = client.parseDOM(item, 'span', attrs={'class': 'd'})[0].strip().lower()
                    if q == 'hd': quality = 'HD'
                    elif 'ts' in q or 'cam' in q: quality = 'CAM'
                    else: quality = 'SD'
                    l = client.parseDOM(item, 'span', attrs={'class': 'c'})[0].strip().lower()
                    if l == 'magyar' or 'szinkron' in l: info = 'szinkron'
                    else: info = ''  
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


