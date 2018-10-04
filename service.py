# -*- coding: utf-8 -*-

"""
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
"""

from resources.lib.modules import log_utils
from resources.lib.modules import control
import threading

control.execute('RunPlugin(plugin://%s)' % control.get_plugin_url({'action': 'service'}))

def syncTraktLibrary():
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.incursion/?action=tvshowsToLibrarySilent&url=traktcollection')
    control.execute(
        'RunPlugin(plugin://%s)' % 'plugin.video.incursion/?action=moviesToLibrarySilent&url=traktcollection')

try:
    AddonVersion = control.addon('plugin.video.exoshark').getAddonInfo('version')
    try:
        RepoVersion = control.addon('repository.exoshark').getAddonInfo('version')
    except:
        RepoVersion = '0'

    log_utils.log('######################### EXOSHARK ############################', log_utils.LOGNOTICE)
    log_utils.log('############ CURRENT EXOSHARK VERSIONS REPORT #################', log_utils.LOGNOTICE)
    log_utils.log('############ EXOSHARK PLUGIN VERSION: %s ###################' % str(AddonVersion), log_utils.LOGNOTICE)
    if not RepoVersion == '0':
        log_utils.log('############ EXOSHARK REPOSITORY VERSION: %s ###############' % str(RepoVersion), log_utils.LOGNOTICE)
    else:
        log_utils.log('############ EXOSHARK REPOSITORY NOT INSTALLED ################', log_utils.LOGNOTICE)
    log_utils.log('###############################################################', log_utils.LOGNOTICE)
except:
    log_utils.log('######################### EXOSHARK ############################', log_utils.LOGNOTICE)
    log_utils.log('############ CURRENT EXOSHARK VERSIONS REPORT #################', log_utils.LOGNOTICE)
    log_utils.log('############ THIS IS NOT AN OFFICIAL EXOSHARK ADDON ###########', log_utils.LOGNOTICE)
    log_utils.log('###############################################################', log_utils.LOGNOTICE)

if control.setting('autoTraktOnStart') == 'true':
    syncTraktLibrary()

if int(control.setting('schedTraktTime')) > 0:
    log_utils.log('###############################################################', log_utils.LOGNOTICE)
    log_utils.log('################## STARTING TRAKT SCHEDULING ##################', log_utils.LOGNOTICE)
    log_utils.log('################## SCHEDULED TIME FRAME %s HOURS ##############' % control.setting('schedTraktTime'), log_utils.LOGNOTICE)
    timeout = 3600 * int(control.setting('schedTraktTime'))
    schedTrakt = threading.Timer(timeout, syncTraktLibrary)
    schedTrakt.start()