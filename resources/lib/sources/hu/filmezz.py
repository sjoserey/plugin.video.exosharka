# -*- coding: utf-8 -*-

import re,urllib,urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import es_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['filmezz.eu']
        self.base_link = 'http://filmezz.eu'
        self.search_link = '/livesearch.php?query=%s&type=0'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            for a in [title, localtitle]:
                try:
                    query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(a))
                    r = client.request(query)
                    result = client.parseDOM(r, 'li')
                    result = [(client.parseDOM(i, 'a')[0], i) for i in result]
                    result = [i for i in result if cleantitle.get(title) == cleantitle.get(i[0].encode('utf-8')) or cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
                    result = [i[1] for i in result if re.search('\s*\((\d{4})\)$', i[0]).group(1) == year]
                    if len(result) > 0: break
                except:
                    pass
            if len(result) == 0: raise Exception()

            url = client.parseDOM(result[0], 'a', ret='href')[0]
            return (url, '', imdb)
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
            if url == None: return            
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote(title))
            r = client.request(query)
            result = r.split('</li>')
         
            result = [i for i in result if 'film.php?' in i]
            result = [i for i in result if '-%s-evad' % season in i]
            if len(result) == 0: raise Exception()
            
            url = client.parseDOM(result, 'a', ret='href')[0]
            return (url, episode, imdb)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            query = urlparse.urljoin(self.base_link, '/' + url[0]).encode('utf-8')
			
            r = client.request(query)
            result = client.parseDOM(r, 'div', attrs={'class': 'sidebar-article details'})[0]
            t = re.findall('imdb"\s*.+?title\/(.+?)\/', result)[0]
            result = [i for i in result if t == url[2]]
            if len(result) == 0: raise Exception()

            result = client.parseDOM(r, 'ul', attrs={'class': 'list-unstyled table-horizontal url-list'})[0]
            result = result.split('<li>')
            result = [i for i in result if urlparse.urljoin(self.base_link, '/link_to.php') in i]

            if url[1].isdigit():
                result = [i for i in result if '>%s. epiz' % url[1] in i]

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for item in result:
                try:
                    host = re.search('/ul>([^<]+)', item).group(1)
                    host = host.strip().lower().rsplit('.', 1)[0]
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = host.encode('utf-8')
                    l = client.parseDOM(item, 'li', ret='class')[0]
                    info = []
                    if l == 'lhun': info.append('szinkron')
                    q = client.parseDOM(item, 'li', ret='class')[1]
                    if 'qcam' in q: quality = 'CAM'
                    elif 'qhd' in q: quality = 'HD'               
                    else: quality = 'SD'
                    url = re.search('\?id=(\d+)', item).group(1).encode('utf-8')
                    url = urlparse.urljoin(self.base_link, '/link_to.php?id=%s' % url)
                    url = url.encode('utf-8')
                    
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False, 'sourcecap': True})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        filmezz_cookie = client.request(url, output='cookie')
        location = ''
        try:
            r = client.request(url, output='headers', redirect=False, cookie=filmezz_cookie).headers
            try: location = [i.replace('Location:', '').strip() for i in r if 'Location:' in i][0]
            except: location = client.request(url, cookie=filmezz_cookie)
            if not location.startswith('http'):
                if 'captcha' in location:
                    captcha_img = self.base_link + '/captchaimg.php'
                    solution = es_utils.captcha_resolve(captcha_img, filmezz_cookie)
                    postdata = urllib.urlencode({'captcha': solution, 'submit': 'Ok'})
                    r = client.request(url, output='headers', redirect=False, cookie=filmezz_cookie, post=postdata).headers
                    try: location = [i.replace('Location:', '').strip() for i in r if 'Location:' in i][0]
                    except: location = client.request(url, cookie=filmezz_cookie)
                    if not location.startswith('http'):
                        location = client.parseDOM(location, 'div', attrs={'align': 'center'})[0]
                        try: location = client.parseDOM(location, 'iframe', ret='src')[0]
                        except: location = client.parseDOM(location, 'IFRAME', ret='SRC')[0]
                else:
                    location = client.parseDOM(location, 'div', attrs={'align': 'center'})[0]
                    try: location = client.parseDOM(location, 'iframe', ret='src')[0]
                    except: location = client.parseDOM(location, 'IFRAME', ret='SRC')[0]
            if not location.startswith('http'): raise Exception()
            url = client.replaceHTMLCodes(location)
            url = re.sub(r'^"|"$', '', url).strip()
            try: url = url.encode('utf-8')
            except: pass
            return location
        except: 
            return