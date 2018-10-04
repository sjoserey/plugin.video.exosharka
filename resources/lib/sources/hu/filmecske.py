# -*- coding: utf-8 -*-

import re,urllib,urlparse,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmecske.hu']
        self.base_link = 'https://filmecske.hu'
        self.search_link = '/film-kereso/itemlist/filterfork2?option=com_k2&view=itemlist&task=filterfork2&format=json&mid=800&Itemid=834&%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            years = cache.get(self.get_years, 720)
            year_id = [i[0] for i in years if year == i[1]][0]

            query = urllib.urlencode({'f[g][text]': localtitle, 'f[g][tags][]': year_id})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            r = client.request(query)
            result = json.loads(r)
            if result['total'] == 0: raise Exception()
   
            result = client.parseDOM(result['items'], 'div', attrs = {'class': 'moduleItemIntrotext'})
            result = [(client.parseDOM(i, 'img', ret='alt')[0].split('- online')[0].strip(), client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [(client.replaceHTMLCodes(i[0]), i[1]) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8')) or cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8'))]
            
            if result:
                url = result[0].encode('utf-8')
                return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            
            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            result = client.parseDOM(r, 'div', attrs = {'class': 'mezo'})
            result = client.parseDOM(result, 'tbody')
            result = client.parseDOM(result, 'td')
            
            for item in result:
                try:
                    url = 'http:' + client.parseDOM(item, 'a', ret='href')[0].split(':')[-1]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    host = url.split('-')[-1].lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = client.parseDOM(item, 'img', ret='src')[0].split('/')[-1].split('.')[0]
                    if q.endswith('K'): quality = 'CAM'
                    else: quality = 'SD'
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': 'szinkron', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            src = client.request(url)
            try: url = client.parseDOM(src, 'iframe', ret='src')[-1]
            except: url = client.parseDOM(src, 'IFRAME', ret='SRC')[-1]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
        
        
    def get_years(self):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link.split('/itemlist')[0])
            years = client.request(query)
            years = client.parseDOM(years, 'select', attrs = {'id': 'field_tags_800'})
            years = client.parseDOM(years, 'option', ret='value'),client.parseDOM(years, 'option')
            years = zip(years[0], years[1])
            return years
        except:
            return
