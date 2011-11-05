import re

import requests
from BeautifulSoup import BeautifulSoup

def hansard_to_json(url):
    '''
    Scrapes hansard from the given URL. Converts it to JSON that contains
    the debate, times and who said things.
    '''

    # TODO Hansards are split into multiple sections, e.g. -0002 is the 2nd part

    r = requests.get(url)
    html = r.content
    soup = BeautifulSoup(html)
    
    content = soup.find(id='maincontent1')

    debate = []
    current_speaker = 'Unknown Speaker'
    current_time = None
    found_time = False

    for child in content:
        if not hasattr(child, 'name'):
            continue
        if child.name == 'p':
            current_speaker = _extract_speaker(child) or current_speaker
            debate.append({
                'speaker': current_speaker,
                'text': _extract_text(child),
                'time': current_time,
            })
        elif child.name == 'h5':
            current_time = _extract_time(child) or current_time
            if current_time and not found_time:
                # The first time the time is set we could have speaking records
                # that are from an unknown timestamp
                for record in debate:
                    record['time'] = current_time
                found_time = True

    from pprint import pprint
    pprint(debate)

    # The start of the actual content is marked by time_0

time_re = re.compile('(([0-9]{1,2})\.([0-9]{1,2}) (am|pm))')
def _extract_time(node):
    for child in node:
        if not child.string:
            continue
        result = time_re.search(child.string)
        if result:
            hour = int(result.groups()[1])
            minute = int(result.groups()[2])
            if result.groups()[3] == 'pm':
                hour += 12
            time = '%d:%02d' % (hour, minute)
            return time
    return None

def _extract_speaker(node):
    '''
    Attempts to extract the speaker from the given node. If no speaker is found
    then None is returned. The speaker is identified by text in two bold 
    sections.
    '''
    for child in node.findAll('b', recursive=False):
        for potential_name in child:
            if not hasattr(potential_name, 'name'):
                return potential_name.string

    return None

def _extract_text(node):
    '''
    Extracts all textual information from the given node. This includes things
    that are in italics or emboldended.
    '''
    text = []
    for child in node:
        if not hasattr(child, 'name'):
            # this must be a text node
            text.append(child.string)
        else:
            text.append(_extract_text(child))
    return ''.join(text)

hansard_to_json('http://www.publications.parliament.uk/pa/cm201011/cmhansrd/cm111102/debtext/111102-0001.htm')
