import json
from datetime import timedelta

from flask import Flask, render_template

from hansard import hansard_tidy

app = Flask(__name__)

@app.route("/hansard/<path:hansard>")
def hansard(hansard):
    hansard_html, times, date = \
            hansard_tidy('http://www.publications.parliament.uk/%s' % hansard)    
    
    # Figure out the start time/date
    start = date + timedelta(minutes=times[0])
    end = date + timedelta(minutes=times[-1])

    tweets = [
        { 'time': '9:35', 
          'screenname': 'colinhowe',
          'profile_pic': 'http://a0.twimg.com/profile_images/142208196/profile_normal.png',
          'body': 'I am really excited about this bill.' },
        { 'time': '9:36', 
          'screenname': 'colinhowe',
          'profile_pic': 'http://a0.twimg.com/profile_images/142208196/profile_normal.png',
          'body': 'I am really excited about this bill.' },
    ]
    return render_template(
            'hansard.html', 
            times=json.dumps(times),
            tweets=json.dumps(tweets),
            hansard_html=hansard_html)

if __name__ == "__main__":
    app.run(debug=True)

