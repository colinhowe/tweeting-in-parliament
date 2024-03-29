from mongoengine import (Document, StringField, IntField, connect, BooleanField)
import csv

connect('parliament')
MEMBER_OUTPUT_ROWS = [
    'name',
    'screen_name',
    'party',
    'constituency_name',
    'twitter_id',
    'constituency_id',
    'theyworkforyou_id',
    'publicwhip_id',
    'dataparliament_id',
    'inactive',
    'protected',
]

class Member(Document):
    name = StringField(required=True)
    screen_name = StringField(required=True, unique=True)
    party = StringField(required=True)
    constituency_name = StringField()

    twitter_id = StringField()
    constituency_id = IntField()
    theyworkforyou_id = IntField()
    publicwhip_id = IntField()
    dataparliament_id = IntField()
    inactive = BooleanField()
    protected = BooleanField()
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

#scripts for getting member data into and out of mongo
def _export():
    writer = csv.DictWriter(open('our_mps.csv', 'wb'), extrasaction='ignore',
                            fieldnames=MEMBER_OUTPUT_ROWS)
    for member in Member.objects:
        writer.writerow(member.to_mongo())

def _initial_import():
    reader = csv.DictReader(open('mps.csv', 'rb'))
    for mp in reader:
        Member.objects.create(
            name=mp['Member Name'],
            screen_name=_sanitize_screen_name(mp['Twitter Screen Name']),
            constituency_name=mp['Constituency Name'],
            party=mp['Party'])
    _update_ids()

_PARTY_MAP = {'Lab': 'Labour',
              'Con': 'Conservative',
              'LDem': 'Liberal Democrats',
         }

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
