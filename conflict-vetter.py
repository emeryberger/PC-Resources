# conflict-vetter.py: finds all stated conflicts from authors and mails them for vetting to reviewers
#   - used for checking for bogus conflicts / conflict engineering.
# Author: Emery Berger <emery.berger@gmail.com>
# Released into the public domain.

import argparse
import csv
import random
import smtplib
import sys
import time
from collections import defaultdict


def my_hash(s):
    """implementation of FNV-1a algorithm"""
    # https://softwareengineering.stackexchange.com/questions/49550/which-hashing-algorithm-is-best-for-uniqueness-and-speed
    # http://www.isthe.com/chongo/tech/comp/fnv/index.html#FNV-param
    h = 2166136261
    for c in s:
        h = h ^ ord(c)
        h = (h * 16777619) % (2**32)
    return h
    
parser = argparse.ArgumentParser("conflict-vetter")
parser.add_argument("--conference", help="conference name, as in pldi-2016")
parser.add_argument("--hashcode", help="hash code, for obscuring paper IDs")
parser.add_argument("--your-name", help="your name goes here, for signing the emails.")
parser.add_argument("--your-email", help="your email goes here, for sending the emails.")
parser.add_argument("--your-password", help="your password goes here, for sending the emails.")

args = parser.parse_args()

if not args.conference or not args.hashcode or not args.your_name:
    parser.print_help()
    sys.exit(-1)

# Change to True to really send mail
reallySendMail = False

senderFirstName = args.your_name
senderName = args.your_name + " <" + args.your_email + ">"
sender = args.your_email
# Assuming you use 2FA, you can generate an App Password for use here at https://security.google.com/settings/security/apppasswords
password = args.your_password # "your-onetime-password-goes-here"
# print(password)

# A map of e-mail to names
# names[e-mail] = name

names = {}
with open(args.conference + '-pcinfo.csv','r') as csvfile:
    reader = csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        key = row['email'].lower()
        value = row['first'] + " " + row['last']
        names[key] = value


# Now we build a list of authors for each paper.
# allAuthors[paper number] = list of authors (by name and e-mail)

allAuthors = defaultdict(list)

with open(args.conference + '-authors.csv','r') as csvfile:
    reader = csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        key = row['paper']
        value = row['first'] + " " + row['last'] + " <" + row['email'] + ">"
        allAuthors[key].append(value)

#
# Now read in the conflicts.
# conflicts[e-mail] = everyone who is on a paper with a stated conflict with e-mail
#

conflicts = defaultdict(list)
conflict_types = defaultdict(lambda: defaultdict(str))

with open(args.conference + '-pcconflicts.csv','r') as csvfile:
    reader = csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        value = list(set(allAuthors[row['paper']]))
        # Filter out institutional conflicts.
        recipient_domain = row['email'].split("@")[1]
        if row['conflicttype'] not in ["Pinned conflict", "Personal", "Other"]:
            continue
        if recipient_domain in ["outlook.com", "yahoo.com", "gmail.com"]:
            pass
        else:
            try:
                if recipient_domain in list(map(lambda name: name.split('<')[1].split("@")[1][:-1], value)):
                    continue
            except:
                pass
        conflicts[row['email']].append((row['paper'], value))
        conflict_types[row['email']][row['paper']] = row['conflicttype']

# Shuffle paper order.
for k in conflicts:
    random.shuffle(conflicts[k])

# Now, we read in all authors.
# We will use this to add noise to the potential conflicts.

authorsList = []
with open(args.conference + '-authors.csv','r') as csvfile:
    reader = csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        key = row['first'] + " " + row['last']
        value = row['email']
        authorsList.append(value)


if reallySendMail:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(sender, password)


if True:
    s = sorted(conflicts.keys())
    msg = ""
    for (count, recipient) in enumerate(s, 1):
        if reallySendMail:
            time.sleep(1) # To avoid Google throttling
        msg = "From: " + senderName + "\nSubject: Conflicts to vet: "
        if (recipient.lower() in names):
            msg += names[recipient.lower()]
        else:
            msg += recipient
        msg += "\n\nHi,\n\n"
        msg += "This mail contains a list of all papers for which you have been marked\nas a conflict. The actual paper numbers have been encrypted.\n\nPlease check each author list to verify that at least one of the authors for\neach paper looks like a legitimate conflict. IF NOT, please enter each one on this form:\n\n  https://forms.gle/sF1gCrGuQz34HiiD7.\n\n"
        # Not actually sampling from random authors right now.
        # r = random.sample(authorsList,5)
        c = conflicts[recipient]
        ind = 1
        for (paper_id, l) in c:
            some_content = False
            uid = str(my_hash(recipient) ^ int(args.hashcode) ^ int(paper_id))
            some_content = True
            msg += str(ind) + ". " + "(UID = " + uid + ") - "
            ctype = conflict_types[recipient][paper_id]
            if ctype == "Pinned conflict":
                ctype = "Auto-detected conflict (probably institutional)"
            msg += ctype + " : "
            i = 0
            for k in l:
                msg += str(k)
                i += 1
                if (i != len(l)):
                    msg += ", "
            msg += "\n"
            ind += 1
        msg += "\n\nThanks,\n" + senderFirstName + "\n"
        msg = msg.encode('utf-8')
        if (reallySendMail):
            print("Sending mail to " + recipient + "...")
            server.sendmail(sender, recipient, msg)
        else:
            print(recipient + "," + str(my_hash(recipient)))

if reallySendMail:
    server.quit()
