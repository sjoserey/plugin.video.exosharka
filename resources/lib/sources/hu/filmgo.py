# -*- coding: utf-8 -*-

import re,urllib,urlparse,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmgo.cc']
        self.base_link = 'https://filmgo.cc'
        self.search_link = '/typeahead/%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(localtitle))
            headers = {'Referer': 'https://filmgo.cc/'}
            r = client.request(query, headers=headers, XHR=True)
            if not r: raise exception()
            result = json.loads(r)

            result = [i for i in result if i['type'] == 'movie']
            result = [i for i in result if cleantitle.get(i['title'].encode('utf-8')) == cleantitle.get(localtitle)]
            if not len(result) == 1: raise Exception()

            url = result[0]['link'].encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            r = client.request(url)

            items = client.parseDOM(r, 'table', attrs={'class': 'table table-striped links-table'})[0]
            items = client.parseDOM(items, 'tbody')[0]
            items = re.findall('(?s)flag\/([\w-]+)\..+?getFavicon\(\'([^\']+).+?<B>([^<>]+)<\/B>.+?<td class="quality">([^<>]+)<\/td>', items)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in items:
                try:
                    host = item[2].lower().replace('www.', '').split('.', 1)[0].strip()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    info = 'szinkron' if item[0] == 'hu-hu' or item[0] == 'lt' else ''
                    q = item[3].lower()
                    if q == 'hd': quality = 'HD'
                    elif 'cam' in q or 'ts' in q or q == 'mozis': quality = 'CAM'
                    else: quality = 'SD'
                    url = client.replaceHTMLCodes(item[1])
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
            return url
