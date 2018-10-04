# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmbaratok.org']
        self.base_link = 'http://filmbaratok.org'
        self.search_link = '/search/?%s'
        self.user = control.setting('filmbaratok.user')
        self.password = control.setting('filmbaratok.pass')

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()
            
            query = urllib.urlencode({'search_query': localtitle, 'tax_release-year[]': year})
            query = urlparse.urljoin(self.base_link, self.search_link % query)
            
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs = {'class': 'resultado'})
            if len(result) == 0: raise Exception()
            result = [(client.parseDOM(i, 'a')[1], client.parseDOM(i, 'a', ret='href')[0]) for i in result]
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
            
            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            cookie = self.get_cookie()

            headers = {'Referer': url, 'Cookie': cookie}

            query = urlparse.urljoin(self.base_link, '/ajax/?q=url-list')
            
            r = client.request(query, headers=headers)
            r = r.decode('unicode-escape').split('<li>')

            for i in r:
                try:
                    host = client.parseDOM(i, 'span', attrs = {'class': 'op'})[0].split('<')[0].rsplit('.', 1)[0].lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    
                    item = re.compile('click&0=([0-9]+).+?Nyelv.+?span>\s?(.+?)<.+?title.+?span>\s?(.+?)<').findall(i)[0]
                    if 'DVD' in item[2]: quality = 'SD'
                    elif 'Mozis' in item[2]: quality = 'CAM'
                    else: quality = 'SD'
                    if 'szinkron' in item[1]: info = 'szinkron'
                    else: info = ''
                    query = urlparse.urljoin(self.base_link, '/online-video/?id=%s' % (item[0]))
                    url = client.replaceHTMLCodes(query)
                    url = url.encode('utf-8')
    
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            cookie = self.get_cookie()
            headers = {'Referer': url, 'Cookie': cookie}
            
            src = client.request(url, headers=headers).lower()
            url = client.parseDOM(src, 'iframe', ret='src')[-1]
            return url
        except:
            return
        
    def get_cookie(self):
        try:
            login = urlparse.urljoin(self.base_link, '/login/')
            post = urllib.urlencode({'log': self.user, 'pwd': self.password, 'submit': 'Belépés', 'redirect_to': 'http://filmbaratok.org'})
            cookie = client.request(login, post=post, output='cookie', close=False)
            if not 'logged_in' in cookie:
                raise Exception()
            return cookie
        except:
            return

