# -*- coding: utf-8 -*-

import re,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['netmozi.com']
        self.base_link = 'https://netmozi.com'
        self.search_link = '/?search=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % imdb)
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'col-sm-4 col_main'})
            if len(result) == 0: raise Exception()

            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr)
            return (url, '', '')
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
            query = urlparse.urljoin(self.base_link, self.search_link % imdb)
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'col-sm-4 col_main'})
            if len(result) == 0: raise Exception()

            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr + '/s%s/e%s' % (season, episode))
            return (url, season, episode)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = client.request(url[0])
            r = client.parseDOM(r, 'div', attrs={'class': 'card-block'})[1]
			
            if url[1].isdigit():
                result = client.parseDOM(r, 'div', attrs={'class': 'tab-pane active'})
                result = [(re.search('<h4.+?>\s*(\w.+)\s*<\/h4>', i).group(1), i) for i in result]
                result = [i[1] for i in result if u'%s. \xe9vad %s. r\xe9sz' % (url[1], url[2]) in i]
                if len(result) == 0: raise Exception()
                r = client.parseDOM(result, 'table', attrs={'class': 'table table-responsive'})[0]

            result = r.split('</tr>')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    itemreg = re.search('(?s)(\/details\/openLink\/\d+).+?td>\s*<td>([^<>]+)<.+?<td>([^<>]+)', item)
                    lreg = re.search('(?s)pic\/(.+?<img src=".+?)\.', item).group(1)
                    host = itemreg.group(3)
                    host = host.rsplit('.', 1)[0].replace('www.', '').strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    q = itemreg.group(2)
                    if 'DVD' in q: quality = 'SD'
                    elif q =='HD': quality = 'HD'
                    elif 'CAM' in q or '(mozis)' in q or q == 'TS': quality = 'CAM'
                    else: quality = 'SD'
                    l = re.sub(r'(?s)(\..+?pic\/)', '', lreg).strip()
                    if l == 'hungarysubtitle' or 'usa' in l or 'uk-hu' in l: info = ''
                    else: info = 'szinkron'
                    url = itemreg.group(1)
                    url = client.replaceHTMLCodes(url)
                    url = self.base_link + url
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            r = client.request(url, output='geturl', redirect=True)
            r = r.rsplit('?l=', 1)[-1].strip()
            r = r.decode('base64')
            url = client.replaceHTMLCodes(r)
            url = url.encode('utf-8')
            return url
        except: 
            return
