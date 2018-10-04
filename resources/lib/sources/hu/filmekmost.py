# -*- coding: utf-8 -*-

import re,urlparse,time,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmekmost.hu']
        self.base_link = 'https://filmekmost.hu'
        self.search_link = '/list.json?version=' + time.strftime("%Y%m%d")


    def movie(self, imdb, title, localtitle, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(query)
            result = json.loads(r)
            
            result = [i['f'] for i in result if (cleantitle.get(title) == cleantitle.get(i['f']['E']) or cleantitle.get(localtitle) == cleantitle.get(i['f']['H']))]
            result = [i for i in result if str(i['y']) == year and i['t'] == 1][0]
            if not result: raise Exception()
            
            E_title = cleantitle.normalize(result['E'].encode('utf-8')).replace(' ', '-').strip().lower()
            if result['E'] == result['H']:
                url = '/online-filmek/' + E_title + '-' + year
            else:
                H_title = cleantitle.normalize(result['H'].encode('utf-8')).replace(' ', '-').strip().lower()
                url = '/online-filmek/' + H_title + '-' + year + '-(' + E_title + ')'
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            query = urlparse.urljoin(self.base_link, url)
            
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs = {'id': 'movie-film-links-button-container'})
            url = client.parseDOM(result, 'a', ret = 'href')[0]
            url = url.encode('utf-8')
            
            r = client.request(url)
            result = client.parseDOM(r, 'div', attrs = {'class': 'series-links-row'})
            if not result: raise Exception()
            
            for i in result:
                try:
                    host = re.search('text sharer\s*["\']\s*>([^<]+)', i).group(1).rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(i, 'div', attrs = {'class': 'icon language'})
                    l = client.parseDOM(l, 'img', ret = 'src')[0]
                    info = 'szinkron' if 'lang_1' in l else ''
                    q = client.parseDOM(i, 'div', attrs = {'class': 'icon quality'})
                    q = client.parseDOM(q, 'img', ret = 'src')[0]
                    quality = 'CAM' if 'quality_7' in q else 'SD'
                    url = client.parseDOM(i, 'a', ret = 'href')[-1]
                    url = url.encode('utf-8')
    
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            r = client.request(url)
            url = client.parseDOM(r, 'iframe', ret = 'src')[0]
            return url.encode('utf-8')
        except:
            return
