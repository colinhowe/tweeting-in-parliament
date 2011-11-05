import requests
from BeautifulSoup import BeautifulSoup
import tablib

PAGES = 24
MEMBERS = []

def scrape():
    for page in range(1, PAGES + 1):
        r = requests.get('http://tweetminster.com/mps/page:%s' % page)
        soup = BeautifulSoup(r.content)
        tweeters = soup.findAll('div', {'class': 'tweeters'})
        for tweeter in tweeters:
            register_member(tweeter)

def register_member(tweeter_div):
    constit_name = tweeter_div.find('h3').text
    title = tweeter_div.find('p', {'class': 'tweetTitle'})
    party = title.find('a').text
    name, screen_name = title.text.split(party)

    print "%s,%s,%s,%s" % (screen_name, name, party, constit_name) 
    MEMBERS.append((constit_name, party, name, screen_name))

if __name__ == '__main__':
    scrape()
    headers = ['Constituency Name', 'Party', 'Member Name', 'Twitter Screen Name']
    data = tablib.Dataset(*MEMBERS, headers=headers)
    with open('mps.csv', 'w') as f:
        f.write(data.csv)
