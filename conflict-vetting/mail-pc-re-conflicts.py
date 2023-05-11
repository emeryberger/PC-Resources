# mail-pc-re-conflicts.py: mail PC members re conflicts that can't be explained
#   - used for checking for bogus conflicts / conflict engineering.
# Authors: Jay Lorch <jaylorch@gmail.com>
#          Emery Berger <emery.berger@gmail.com>
# Released into the public domain.

import argparse
import csv
import re
import smtplib
import sys
import os
import time
from collections import defaultdict

parser = argparse.ArgumentParser('mail-pc-re-conflicts', epilog="""
Normally, this script is used as follows:

First, a chair runs the explain-conflicts script to obtain a list of
unexplained conflicts in a file named *-unexplainedconflicts.csv.

Then, the chair manually looks over the unexplained-conflicts file to
remove any they understand and can explain.

Then, the chair runs this mail-pc-re-conflicts.py script to ask PC
members to look over the unexplained conflicts and confirm ones that
they also can't explain.  The chairs wait for a while for the PC to
respond.

Finally, the chair runs the investigate-conflicts.py script to
get a list of unexplained conflicts that PC members report, so they
can investigate.
""")
parser.add_argument('--conference', help='conference name used as a prefix of csv file names exported by HotCRP, e.g., osdi21', required=True)
parser.add_argument("--form-url", help="URL for the form recipients should fill out, e.g., https://forms.gle/sF1gCrGuQz34HiiD7", required=True)
parser.add_argument("--sender-name", help="Sender name goes here, for the To line of the emails.", required=True)
parser.add_argument("--sender-email", help="Sender email goes here, for sending the emails.", required=True)
parser.add_argument("--sender-password", help="Sender password goes here, for sending the emails via gmail.  If you use 2FA for Google, you can generate an App Password for use here at https://security.google.com/settings/security/apppasswords", required=True)
parser.add_argument("--reply-to", help="(optional) email where people should reply to, if different from your email")
parser.add_argument("--subject", help="(optional) subject line for emails; if you don't supply this parameter, the subject will be 'Conflics to vet'")
parser.add_argument("--signature", help="(optional) signature; if you don't supply this parameter, it will be the sender name")
parser.add_argument("--deadline", help="(optional) when PC members should fill out the form by; if you don't supply this parameter, the email won't specify a deadline")
parser.add_argument("--cc", help="(optional) email address to cc on each email")
parser.add_argument("--really-send", help="actually send mail, don't just print all the mails that would be sent", action="store_true")

def describe_how_to_get_pcinfo(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/users?t=pc (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select people (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "PC info" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-pcinfo.csv file downloaded this way to this directory.')

def describe_how_to_get_authors(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/search?q=&t=act (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select papers (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "Authors" from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-authors.csv file downloaded this way to this directory.')

class Conflict:
    def __init__(self, paper_id, pcmember, uid, conflict_type):
        self.paper_id = paper_id
        self.pcmember = pcmember
        self.uid = uid
        if conflict_type == "Pinned conflict":
            self.conflict_type = "Auto-detected conflict (probably institutional)"
        else:
            self.conflict_type = conflict_type


class PCMember:
    def __init__(self, first, first_last, email):
        self.first = first
        self.first_last = first_last
        self.email = email
        self.conflicts = []

    def add_conflict(self, conflict):
        self.conflicts.append(conflict)

    def get_conflicts_in_uid_order(self):
        return sorted(self.conflicts, key=(lambda conflict : int(conflict.uid)))


class EmailSender:
    def __init__(self, conference, form_url, sender_name, sender_email, sender_password, reply_to, subject, signature, deadline, cc, really_send):
        self.conference = conference
        self.form_url = form_url
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.sender_name_and_email = sender_name + " <" + sender_email + ">"
        self.sender_password = sender_password
        self.reply_to = reply_to
        self.subject = subject if subject else "Conflicts to vet"
        self.signature = signature if signature else sender_name
        self.deadline = deadline
        self.cc = cc
        self.send_mail = really_send
        self.pcinfo = {}
        self.paper_authors = defaultdict(list)

    def run(self):
        self.get_pcemails()
        self.get_authors()
        self.get_conflicts()
        if self.send_mail:
            self.initialize_server()
        self.send_emails()
        if self.send_mail:
            self.server.quit()
        else:
            print("*** No mails sent. To send mails, use --really-send ***")

    def get_pcemails(self):
        infile_name = self.conference + "-pcinfo.csv"
        if not os.path.exists(infile_name):
            describe_how_to_get_pcinfo(self.conference, infile_name)
            sys.exit(-1)

        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                first = row["first"]
                last = row["last"]
                first_last = first + " " + last
                email = row["email"]
                self.pcinfo[email] = PCMember(first, first_last, email)

    def get_authors(self):
        infile_name = self.conference + "-authors.csv"
        if not os.path.exists(infile_name):
            describe_how_to_authors(self.conference, infile_name)
            sys.exit(-1)

        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile, delimiter=',')
            for row in reader:
                paper_id = row["paper"]
                affiliation = row["affiliation"]
                if not affiliation:
                    affiliation = "no affiliation provided"
                self.paper_authors[paper_id].append("%s %s (%s) <%s>" % (row["first"], row["last"], affiliation, row["email"]))

    def get_conflicts(self):
        infile_name = self.conference + "-unexplainedconflicts.csv"
        if not os.path.exists(infile_name):
            print("You need to run explain-conflicts.py before using this script.")
            sys.exit(-1)

        with open(infile_name, 'r') as infile:
            reader = csv.DictReader(infile,delimiter=',')
            for row in reader:
                pcmember = row["email"]
                paper_id = row["paper"]
                if pcmember not in self.pcinfo:
                    print("Conflict found for PC member %s, but no email found for them" % (pcmember))
                    sys.exit(-1)
                elif paper_id not in self.paper_authors:
                    print("Conflict found for paper %s, but no authors found for it" % (paper_id))
                    sys.exit(-1)
                else:
                    self.pcinfo[pcmember].add_conflict(Conflict(paper_id, pcmember, row["uid"], row["conflicttype"]))

    def initialize_server(self):
        print("Opening connection to SMTP server")
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.sender_email, self.sender_password)
        print("Connection opened successfully")

    def send_emails(self):
        for name,pcmember in self.pcinfo.items():
            self.send_single_email(pcmember)

    def send_single_email(self, pcmember):
        conflicts = pcmember.get_conflicts_in_uid_order()
        if self.send_mail:
            time.sleep(2) # To avoid Google throttling

        recipient = pcmember.email
        if self.send_mail:
            print("Preparing email for %s" % (recipient))
        msg = "To: %s\nFrom: %s\nSubject: %s - %s\n" % (recipient, self.sender_name_and_email, self.subject, pcmember.first_last)
        if self.cc is not None:
            msg += "Cc: %s\n" % (self.cc)
        if self.reply_to is not None:
            msg += "Reply-To: %s\n" % (self.reply_to)

        msg += "\nHi, %s--\n" % (pcmember.first)
        msg += """
This mail contains a list of all your unexplained conflicts. An unexplained conflict is a case where the authors marked you as a conflict, but our script couldn't find an explanation for why. That script bases its findings on the conflict list you put in your HotCRP profile.

The paper numbers have been encrypted as UIDs and the list below is in order by UID.

Please check each author list to verify that at least one of the authors in it looks like a legitimate conflict. IF NOT, please enter each UID that doesn't look like a legitimate conflict in this form:  %s

You don't need to report conflicts that you recognize as legitimate. And you don't have to reply to this email; just use the form. There's also no need for you to do any detailed investigation of possibly-invalid conflicts. You can just put their UIDs in the form and leave the investigation to us.

""" % (self.form_url)

        if self.deadline and len(conflicts) > 0:
            msg += "Please check these conflicts (and, if needed, fill out the form) before %s. Better yet, do it now; it should only take a couple of minutes.\n\n" % (self.deadline)
        if len(conflicts) == 0:
            msg += "(Empty list - You have no unexplained conflicts, so you don't need to do anything.)\n"
        for conflict in conflicts:
            authors = ", ".join(self.paper_authors[conflict.paper_id])
            msg += "(UID = %s) - %s : %s\n\n" % (conflict.uid, conflict.conflict_type, authors)
        msg += "\nThanks!\n--%s\n" % (self.signature)
        if self.send_mail:
            msg = msg.encode('utf-8')
            print("Sending mail to %s" % (recipient))
            self.server.sendmail(self.sender_email, recipient, msg)
            print("Mail sent to %s" % (recipient))
        else:
            print("***\n\nIf you run with --really-send, the following will be sent to %s:\n%s" % (recipient, msg))

args = parser.parse_args()

mail_sender = EmailSender(args.conference, args.form_url, args.sender_name, args.sender_email,
                          args.sender_password, args.reply_to, args.subject, args.signature,
                          args.deadline, args.cc, args.really_send)
mail_sender.run()
