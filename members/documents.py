from mongoengine import (Document, StringField, IntField, connect)

connect('parliament')

class Member(Document):
    name = StringField(required=True)
    screen_name = StringField(required=True, unique=True)
    party = StringField(required=True)
    constituency_name = StringField()

    twitter_id = StringField(unique=True)
    constituency_id = IntField()
    theyworkforyou_id = IntField()
    publicwhip_id = IntField()
    dataparliament_id = IntField()
    meta = {
        'indexes': ['screen_name', ]
    }

def _sanitize_screen_name(screen_name):
    if not screen_name:
        return None
    if screen_name.startswith('@'):
        screen_name = screen_name[1:]
    return screen_name.lower()

def _sanitize_publicwhip_id(input):
    return input.split('/')[-1]

#scripts for  getting member data into mongo
def _initial_import():
    import csv
    reader = csv.DictReader(open('mps.csv', 'rb'))
    for mp in reader:
        Member.objects.create(
            name=mp['Member Name'],
            screen_name=_sanitize_screen_name(mp['Twitter Screen Name']),
            constituency_name=mp['Constituency Name'],
            party=mp['Party'])

_PARTY_MAP = {'Lab': 'Labour',
              'Con': 'Conservative',
              'LDem': 'Liberal Democrats',
         }
    _update_ids()

def _update_ids():
    import csv
    reader = csv.DictReader(open('members_with_ids.csv', 'rb'))
    for mp in reader:
        screen_name = _sanitize_screen_name(mp['twitter'])
        if not screen_name:
            continue
        try:
            member = Member.objects.get(screen_name=screen_name)
            publicwhip_id = _sanitize_publicwhip_id(mp['url'])
            print 'adding publicwhip id %s to %s' % (publicwhip_id, screen_name)
            member.publicwhip_id = publicwhip_id
            member.save()
        except Member.DoesNotExist:
            print 'creating %s' % screen_name
            party = mp['party']
            if party in _PARTY_MAP:
                party = _PARTY_MAP[party]
            Member.objects.create(
                name='%s %s' % (mp['firstname'], mp['lastname']),
                publicwhip_id=_sanitize_publicwhip_id(mp['url']),
                party=party,
                screen_name=screen_name)
