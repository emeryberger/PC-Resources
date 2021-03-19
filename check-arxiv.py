# Some conferences have blackout periods for posting papers on
# arxiv. This script checks a list of paper titles (via stdin) on arxiv to see if they are within a conference blackout period.

# Emery Berger, https://emeryberger.com
# Released into the public domain.

import datetime
import sys
import urllib.request
import xmltodict
from dateutil.parser import parse

# Submission date
submission_date = parse('2020-01-01T23:59:59Z')
# Delta, before and after (here, two weeks)
delta = datetime.timedelta(days=14)
blackout_before = submission_date - delta
blackout_after = submission_date + delta

for line in sys.stdin:

    # Trim any leading or trailing spaces.
    line = line.rstrip()
    line = line.lstrip()

    title = line
    # Make the title safe to use in the arxiv URL request.
    safe_title = urllib.parse.quote_plus(title)

    # Get data about this title.
    with urllib.request.urlopen(f'http://export.arxiv.org/api/query?search_query=ti:"{safe_title}"') as f:
        # Read the results from Arxiv
        result = f.read().decode('utf-8')
        # Parse into a dict
        result_dict = xmltodict.parse(result)
        # Check the published date.
        try:
            published_date = parse(result_dict["feed"]["entry"]["published"])
            if published_date >= blackout_before and published_date <= blackout_after:
                print("**WITHIN BLACKOUT PERIOD**: ", title, result_dict["feed"]["entry"]["id"])
            else:
                print("OK: ", title)
        except:
            print("Title not found: ", title)
            pass
    
    
    
