# -*- coding: utf-8 -*-

import re,urllib,urlparse,json
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['onlinefilmpont.site']
        self.base_link = 'http://onlinefilmpont.site'
        self.search_link = '/wp-json/keremiya/search/?keyword=%s&nonce=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            r = client.request(self.base_link)
            result = re.search('var sL10n\s*=\s*([^;]+)', r).group(1)
            result = json.loads(result)
            nonce = result['nonce'].encode('utf-8')
            
            query = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote(localtitle), nonce))
            r = client.request(query)
            result = json.loads(r)
            result = result.items()
            result = [i[1] for i in result if cleantitle.get(i[1]['title'].encode('utf-8')) == cleantitle.get(localtitle)]
            result = [i for i in result if i['extra']['date'].encode('utf-8') == year]

            if not result: raise Exception()

            url = result[0]['url'].encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            r = client.request(url)
            tag = client.parseDOM(r, 'div', attrs = {'class': 'video-container'})
            tag = client.parseDOM(tag, 'p')[-1].lower()
            
            url = client.parseDOM(r, 'div', attrs = {'class': 'single-content tabs'})
            url = client.parseDOM(url, 'a', ret='href')[0]
            url = url.encode('utf-8')
            
            post = urllib.urlencode({'lock_password': '', 'Submit': 'Online Linkek'})
            r = client.request(url, post=post)

            result = client.parseDOM(r, 'a', ret = 'href')
            result += client.parseDOM(r.lower(), 'iframe', ret='src')
            result = [i for i in result if not 'youtube.com' in i]
            if not result: raise Exception()
            
            info = '' if 'feliratos' in tag else 'szinkron'
            quality = 'CAM' if ('cam' in tag or 'mozis' in tag or u'kamer\u00E1s' in tag) else 'SD'

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = re.search('(?:\/\/|\.)([^www][\w]+[.][\w]+)\/', item).group(1)
                    host = host.strip().lower().split('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item.encode('utf-8')
                    if quality == 'SD': quality = source_utils.check_sd_url(url)
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url
