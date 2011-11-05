import memcache
import re
import requests
from datetime import datetime

from BeautifulSoup import BeautifulSoup

import settings

mc = memcache.Client([settings.MEMCACHE], debug=0)

def hansard_tidy(url):
    '''
    Takes a Hansard from a given URL and extracts out the main content.
    Also, adds IDs to every time element and extracts out the times they are
    associated with.
    '''
    cache_key = 'url_cache_%s' % hash(url)
    content = mc.get(cache_key)
    if not content:
        content = requests.get(url).content
        mc.set(cache_key, content)

    soup = BeautifulSoup(content)
    debate_html = soup.find(id='content-small')
    _remove_href(debate_html)
    times = _give_times_ids(debate_html)
    date = _get_date(debate_html)
    
    return unicode(debate_html), times, date

def _get_date(soup):
    for node in soup.findAll('notus-date'):
        day = int(node['day'])
        month = int(node['month'])
        year = int(node['year'])
        return datetime(year, month, day)
    raise Exception('No date found :(')

def _remove_href(soup):
    '''
    Removes all <a href..> nodes from the given soup.
    '''
    for node in soup:
        if getattr(node, 'name', '') == 'a':
            try:
                if node['href']:
                    node.extract()
            except KeyError:
                pass
        elif hasattr(node, 'name'):
            _remove_href(node)

time_re = re.compile('([1-9][0-9]?).([0-5][0-9]) (am|pm)')
def _give_times_ids(soup):
    times = []
    for node in soup:
        if not node.string:
            continue
        result = time_re.match(node.string)
        if result:
            hour = int(result.groups()[0])
            minute = int(result.groups()[1])
            if result.groups()[2] == 'pm' and hour != 12:
                hour += 12
            minute_since_midnight = hour * 60 + minute
            times.append(minute_since_midnight)
            node['id'] = 'time_%s' % minute_since_midnight
    return times
