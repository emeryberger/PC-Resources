# PC-Resources

A collection of resources for Program Committee chairs.

## [Scripts for Managing a PC meeting over Zoom](PC-meeting-scripts/)

See the directory [PC-meeting-scripts/](PC-meeting-scripts/).

## [Reviewing guidelines for Program Committee members (for PLDI'16)](https://emeryblogger.com/2018/03/22/reviewing-guidelines-for-program-committee-members/)

## [Instructions for Authors for Author Responses (for ASPLOS'21)](asplos21-instructions-for-author-response.md)

## [Check arXiv for blackout period violations](check-arxiv.py)

The script [check-arxiv.py](check-arxiv.py) makes it easy to check
arXiv for papers that violate a blackout period (if your conference
has one). Takes as input a list of titles (via stdin) and outputs
violations.  Currently you need to modify the script to set the
submission date and optionally change the delta (time before and after
the submission date).


## Conflict vetting

`conflict-vetter.py` finds all stated conflicts from authors and mails them for vetting to reviewers
  - used for checking for bogus conflicts / conflict engineering.
  

You will probably need to install bcrypt:
```
% python3 -m pip install bcrypt
```

To use this script for your conference, you first need to download the following files from HotCRP:
  - `confname-pcinfo.csv`
     - go to [https://confname.hotcrp.com/users?t=pc](https://confname.hotcrp.com/users?t=pc)
     - scroll to the bottom, select all, click download, and choose "PC info".
  - `confname-authors.csv`
     - go to [https://confname.hotcrp.com/search?q=&t=s](https://confname.hotcrp.com/search?q=&t=s)
     - scroll to the bottom, select all, click download, and choose "Authors".
  - `confname-pcconflicts.csv`
     - go to [https://confname.hotcrp.com/search?q=&t=s](https://confname.hotcrp.com/search?q=&t=s)
     - scroll to the bottom, select all, click download, and choose "PC conflicts".

You need to the run the script with a number of options, specified at the command line.
The command will look something like this:

```
% python3 conflict-vetter.py --conference asplos21 --hashcode hellokitty --your-name "Emery Berger" --your-email "emery.berger@gmail.com" --your-password goodbyedoggy --form-url "https://forms.gle/someform"
```

If you are using 2FA for Google mail, you can generate an App Password for use here: [https://security.google.com/settings/security/apppasswords](https://security.google.com/settings/security/apppasswords)

**NOTE**: this script will only actually send mail if you explicitly add the command-line option `--really-send`.

As a side effect, this command produces an output file `uidmap.csv`, which you can use to reverse-lookup
paper numbers from generated (encrypted) paper uids.

## Alternate conflict-vetting scripts

The `conflict-vetting/` directory contains scripts supporting a slightly different way of vetting conflicts. This approach differs from that of conflict-vetter.py in three main ways:

* It uses more data to try to explain conflicts. For instance, it trusts and uses the conflict information each PC member enters on their HotCRP profile page. Also, it lets the chair create a CSV file including extra affiliations the chair is aware that authors have. For instance, if the chair knows that JohnDoe@email.com worked at Acheron University last year, the chair can put `JohnDoe@email.com,"Acheron University"` in the CSV file.

* It breaks the process into multiple steps. Instead of finding unexplained conflicts and immediately emailing them all to PC members, it uses two scripts for this. The first script finds unexplained conflicts and puts them in a CSV file. The second script reads that CSV file and emails about it to PC members. This lets the chair manually inspect and edit the file in between, e.g., to remove conflicts they understand but the script doesn't.

* If it can't find a HotCRP file it needs (e.g., `confname-pcinfo.csv`), it prints an error message with instructions explaining how to download the missing file from HotCRP.

A chair uses the scripts in `conflict-vetting/` as follows:

1. The chair makes a file `confname-extraaffiliations.csv` where `confname` is the conference name, listing any extra affiliations that they know about for paper authors. If they know of no such extra affiliations, they can skip this step. The first line of that csv file should be the following literal text:
```
email,affiliation
```

2. The chair runs the `explain-conflicts.py` script to obtain a list of unexplained conflicts in a file named `confname-unexplainedconflicts.csv` and a list of explained conflicts in a file named `confname-explainedconflicts.csv`.  An example command line is:
```
python3 explain-conflicts.py --conference=osdi21 --hash-salt=hellokitty
```

3. The chair manually looks over the unexplained-conflicts file to remove any they understand and can explain.

4. The chair creates a Google Forms form allowing PC members to submit the UIDs of unexplained conflicts that even they can't explain.  This should be a form with just two fields: the PC member's email and a list of space-separated UIDs.  (Don't request comma-separated UIDs, since the use of commas with long integers confuses Google's input parsing.)

5. If the chair is using 2FA for Google mail, they generate an App Password for use here: [https://security.google.com/settings/security/apppasswords](https://security.google.com/settings/security/apppasswords)

6. The chair runs the `mail-pc-re-conflicts.py` script to ask PC members to look over the unexplained conflicts and confirm ones that they also can't explain.  An example command line is:
```
python3 mail-pc-re-conflicts.py --conference=osdi21 --sender-name="Jay Lorch" --sender-email="jaylorch@gmail.com" --sender-password="abcdefghijklmnop" --reply-to="osdi21chairs@usenix.org" --subject="[OSDI '21] Conflicts to vet" --form-url="https://forms.gle/whatevergooglegivesyou" --signature="Angela Demke Brown and Jay Lorch, OSDI '21 co-chairs" --deadline="3pm Pacific on December 7" --cc="osdi21chairs@usenix.org"
```

NOTE:  This will print the emails to standard output, but won't actually send any emails. If the chair is happy with these, they should rerun the above command with the extra argument `--really-send`.

7. The chair emails all the PC members via HotCRP telling them to look in their inboxes for the email asking for confirmation of unexplained conflicts, and to check their junk-mail folders if they don't see it. This is useful because PC members have likely whitelisted the HotCRP mail server, but not necessarily the personal email used to send these emails.

8. The chair waits for a while for the PC to respond.  After the PC members report the UIDs for conflicts they also can't explain, the chair manually uses the Google Forms responses to create a CSV file `confname-reported-uids.csv` file whose first line is:
```
email,uid
```
and whose each subsequent line is a PC member's email, a comma, and either a single UID or a space-separated list of UIDs.

9. The chair runs the `investigate-conflicts.py` script to convert these into a decrypted list of conflicts to investigate.  An example command line is:
```
python3 investigate-conflicts.py osdi21-unexplainedconflicts.csv osdi21-reported-uids.csv
```

10. If the chair began the conflict-vetting process before the final submission deadline (e.g., after the abstract-registration deadline), they may want to do it again after the final submission deadline.  After all, authors may declare more improper conflicts up until that deadline.  So, after the paper-submission deadline (when authors can't change their conflicts any more), the chair runs `find-unexplained-conflicts.py` one more time to get another file, e.g., `10dec/osdi21-unexplainedconflicts.csv`.  The chair then runs the `diff-unexplained-conflicts.py` script to get a list of just the unexplained conflicts from the latter file.  An example command line is:
```
python3 diff-unexplained-conflicts.py 4dec/osdi21-unexplainedconflicts.csv 10dec/osdi21-unexplainedconflicts.csv
```

## Concurrent submission checker

Chairs of two conferences with overlapping review periods can use this tool to check for potential concurrent submission of the same work to both conferences.  This way, they can tell which authors may need reminding that concurrent submission isn't permitted.

To avoid over-sharing between the cooperating chairs, it hashes the titles of all submissions.  This way, a chair only has to email the other chair a file containing paper IDs and hashes.  To hash a title, the script removes all non-alphanumeric characters, converts to uppercase, then applies SHA-256.

This tool is only meant to detect inadvertent, not malicious, concurrent submission.  Authors can easily avoid detection by this script by using slightly different wording in their two titles.

Chairs use the `concurrent-submission-checker.py` script as follows:

1. The chair of the first conference runs it to get title hashes, then sends the resulting file to the chair of the second conference as the script instructs them to.  An example command line is:
```
python3 concurrent-submission-checker.py fast21
```

2. The chair of the second conference runs it to get title hashes, then runs it again with `--other-conference` to compare the two sets of title hashes. The output from that latter run will describe the potential instances of concurrent submission.  For instance, the chair might run:
```
python3 concurrent-submission-checker.py osdi21
python3 concurrent-submission-checker.py osdi21 --other-conference=fast21
```

## Topic preference checker

The `find-topicless.py` script prints a list of all PC members who haven't yet selected any topic preferences.  An example command line is:
```
python3 find-topicless.py osdi21
```

If a PC member has set at least one topic preference, the output won't include them.

## Format checker

The `format-checking/format-checker.py` script generates files to help a chair scan for obvious formatting violations in submitted papers.  A sample command line is:
```
cd format-checking
python3 format-checker.py osdi21 --page-limit=12 --output-prefix=output/
```

It generates the following files in the directory `output/`:
* `all_first_pages.pdf` contains the first pages of all submissions.  This is useful to scan for accidental inclusion of author names and affiliations in a conference where submissions should be blind.
* `all_papers_stenciled.pdf` contains the first, `n`th, and `n+1`st pages of all submissions, where `n` is the page limit.  These pages are overlayed with a stencil showing vertical 12-point-high stripes, so that one can visually inspect for papers that use leading that isn't 12-point.  The stencils on the `n+1`st pages are red instead of blue, allowing the chair to scan for cases where the paper material continues beyond the page limit.
* For each submission, a file containing the stenciled version of just that submission.

## Review sizer

The `review-sizer.py` script generates a file `reviews_by_count.html` listing all reviews from shortest to longest. The chair can view this in a browser to check for insufficient reviews and prod their authors to expand them.  A sample command line is:
```
python3 review-sizer.py osdi21
```

If you want to customize the fields to include in the count, use the `--fields` command-line argument to specify the field name selector as a regular expression.  The default is as if you included `--fields "[cC]omment|[sS]trength|[wW]eakness|[qQ]uestion"`.

## Statistics reporter for chair message

Chairs are often called upon to write a "Message from the Chair" for inclusion in the proceedings.  Such a message often contains statistics about the reviews and online discussions.  These two scripts produce such statistics.

The `comment-word-counter.py` script reports statistics about the comments PC members posted as part of discussions (not as part of review forms).  It reports how many comments there were, as well as how many total words there were in those comments.
A sample command line is:
```
python3 comment-word-counter.py osdi21
```

The `review-word-counter.py` script reports how many words were in the reviews PC members submitted.  Note, however, that it uses a downloaded zip file of reviews, and that zip file doesn't include reviews for papers the downloader is conflicted with.  A sample command line is:
```
python3 review-word-counter.py osdi21
```

If you want to customize the fields to include in the count, use the `--fields` command-line argument to specify the field name selector as a regular expression.  The default is as if you included `--fields "[sS]ummary|[cC]omment|[sS]trength|[wW]eakness|[qQ]uestion"`.
