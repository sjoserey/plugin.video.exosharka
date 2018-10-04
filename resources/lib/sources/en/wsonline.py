# -*- coding: utf-8 -*-

'''
    ExoShark Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''



import re,urllib,urlparse,json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import debrid


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['watchseries-online.be']
        self.base_link = 'https://watchseries-online.be'
        self.useragent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode']))

            url = self.base_link + '/episode/%s' % cleantitle.geturl(query)

            r = client.request(url)

            items = re.findall('(?s)tr class="(?:odd|even)">.+?href="([^"]+)', r)
            if items == []: return sources

            hostDictTot = hostDict + hostprDict

            for item in items:
                try:
                    if 'go4up.com' in item:
                        if not debrid.status(): raise Exception()
                        try:
                            headers = {'User-Agent': self.useragent}
                            url = item.replace('//go4up', '//dl.go4up')
                            r = client.request(url, headers=headers)
                            rf = re.findall('url\:\s*"([^"]+)"', r)[0]
                            urlr = 'https://go4up.com' + rf
                            r1 = client.request(urlr, headers=headers)
                            r1 = r1.strip()
                            # try:
                                # if not info: info = []
                                # size = re.findall('center>\s*<h3>.+?((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB)).+?<\/h3', r)[0]
                                # div = 1 if size.endswith(('GB', 'GiB')) else 1024
                                # size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                                # size = '%.2f GB' % size
                                # info.append(size)
                            # except:
                                # pass
                            items1 = json.loads(r1)
                            for i in items1:
                                link = i['link']
                                link = re.findall('">([^<>]+)<\/a', link)[0]
                                url = link.strip()
                                hostnum = url.rsplit('/', 1)[-1]

                                if hostnum == '2': hoster = 'uptobox'
                                elif hostnum == '4': hoster = 'filerio'
                                elif hostnum == '5': hoster = 'depositfiles'
                                elif hostnum == '6': hoster = '2shared'
                                elif hostnum == '12': hoster = 'filefactory'
                                elif hostnum == '13': hoster = 'uploaded.net'
                                elif hostnum == '17': hoster = 'turbobit'
                                elif hostnum == '18': hoster = 'free'
                                elif hostnum == '33': hoster = 'rapidgator'
                                elif hostnum == '34': hoster = 'share-online'
                                elif hostnum == '35': hoster = '4shared'
                                elif hostnum == '36': hoster = 'sendspace'
                                elif hostnum == '41': hoster = 'hitfile'
                                elif hostnum == '42': hoster = 'zippyshare'
                                elif hostnum == '43': hoster = '1fichier'
                                elif hostnum == '50': hoster = 'mega'
                                elif hostnum == '55': hoster = 'uppit'
                                elif hostnum == '57': hoster = 'tusfiles'
                                elif hostnum == '61': hoster = 'solidfiles'
                                elif hostnum == '64': hoster = 'filepup'
                                elif hostnum == '65': hoster = 'oboom'
                                elif hostnum == '68': hoster = 'bigfile'
                                elif hostnum == '76': hoster = 'userscloud'
                                elif hostnum == '78': hoster = 'filecloud'
                                elif hostnum == '80': hoster = 'openload'
                                elif hostnum == '82': hoster = 'speedvideo'
                                elif hostnum == '83': hoster = 'nitroflare'
                                elif hostnum == '85': hoster = 'clicknupload'
                                elif hostnum == '87': hoster = 'uploadboy'
                                elif hostnum == '90': hoster = 'rockfile'
                                elif hostnum == '91': hoster = 'faststore'
                                elif hostnum == '92': hoster = 'salefiles'
                                elif hostnum == '94': hoster = 'downace'
                                elif hostnum == '95': hoster = 'datafile'
                                elif hostnum == '97': hoster = 'katfile'
                                elif hostnum == '98': hoster = 'uploadgig'
                                elif hostnum == '99': hoster = 'owndrives'
                                elif hostnum == '100': hoster = 'cloudyfiles'

                                valid, host = source_utils.is_host_valid(hoster, hostDictTot)
                                if valid:
                                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': True})
                        except:
                            pass

                    valid, hoster = source_utils.is_host_valid(item, hostprDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': True})

                    valid, hoster = source_utils.is_host_valid(item, hostDict)
                    urls, host, direct = source_utils.check_directstreams(item, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        if 'go4up.com' in url:
            try:
                url = re.sub('https', 'http', url)
                url = re.sub('//go4up', '//dl.go4up', url)
                headers = {'User-Agent': self.useragent}
                r = client.request(url, headers=headers)
                r = client.parseDOM(r, 'div', attrs={'id': 'linklist'})[0]
                url = client.parseDOM(r, 'a', ret='href')[0]
            except:
                return
        return url
