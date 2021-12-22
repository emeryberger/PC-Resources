#!/usr/bin/env python3
#   - used for sorting reviews by number of words
# Authors: Jon Howell <jonh@jonh.net>
#          Jay Lorch <jaylorch@gmail.com>
# Released into the public domain.

from collections import defaultdict
import argparse
import os
import re
import sys
import zipfile

parser = argparse.ArgumentParser('review-sizer', epilog="""
This script takes reviews written for submissions to a
conference and reports all their sizes, from shortest to
longest.
""")
parser.add_argument('conference', help='conference name used as a prefix of -reviews.zip file name exported by HotCRP, e.g., osdi21')
parser.add_argument('--fields', help="regular expression for review fields to include, default '[cC]omment|[sS]trength|[wW]eakness|[qQ]uestion'", default='[cC]omment|[sS]trength|[wW]eakness|[qQ]uestion', type=str)

def describe_how_to_get_reviews(conference, file_name):
    print('Could not find a file in the current directory named ' + file_name)
    print('To get this file, do the following:')
    print('1) Visit https://' + conference + '.usenix.hotcrp.com/search?q=&t=s (the domain might be different for a non-USENIX conference).')
    print('2) Scroll to the bottom of the page.')
    print('3) Look for "Select papers (or select all X)" and click "select all X".')
    print('4) To the right of that, after "Download", select "All review forms (zip)" under Review assignments [DO NOT PICK "Reviews (zip)" under Reviews] from the dropdown menu.')
    print('5) Click the "Go" button to the right of that dropdown.')
    print('6) Copy the ' + conference + '-reviews.zip file downloaded this way to this directory.')

class ReviewSizer:
    def __init__(self, conference, fields):
        self.conference = conference
        self.fields = fields

    def parse(self, paper_file):
        cur_review = None
        cur_field = None
        for line in paper_file.split('\n'):
            line = line.strip()
            mo = re.search("^==\+== Begin Review #(.*)", line)
            if mo:
                cur_review = mo.groups()[0]
                cur_field = None
                # If it doesn't have a letter in it, it's a draft review and we should ignore it
                if not re.search("[A-Z]", cur_review):
                    cur_review = None
            else:
                mo = re.search("^==\*== (.+)", line)
                if mo:
                    cur_field = mo.groups()[0]
                    # Ignore any fields that we aren't looking for
                    if not re.search(self.fields, cur_field):
                        cur_field = None
                elif re.search("^==\+== Scratchpad", line):
                    cur_field = None
                elif cur_review and cur_field and not line.startswith("="):
                    self.by_review[cur_review] += line + "\n"
    
    def run(self):
        self.by_review = defaultdict(str)
        file_name = self.conference + "-reviews.zip"
        if not os.path.exists(file_name):
            describe_how_to_get_reviews(self.conference, file_name)
            sys.exit(-1)
        zf = zipfile.ZipFile(file_name)
        for name in zf.namelist():
            contents = zf.read(name).decode("utf-8")
            self.parse(contents)
        by_word_count = [(len(v.split()), k, v) for k,v in self.by_review.items()]
        by_word_count.sort()
        file_name = "reviews_by_count.html"
        ofp=open(file_name, "w")
        for count,review,body in by_word_count:
            paper = int(re.search("(\d+)", review).groups()[0])
            ofp.write('<br><a href="https://%s.usenix.hotcrp.com/paper/%s#r%s">%s (%s words)</a>\n<blockquote>%s</blockquote>' % (self.conference, paper, review, review, count, body.replace('\n', "<p>\n")))
        ofp.close()
        print("Output written to " + file_name)
        #print([(k, len(v.split())) for k,v in self.by_review.items()])

args = parser.parse_args()
sizer = ReviewSizer(args.conference, args.fields)
sizer.run()
