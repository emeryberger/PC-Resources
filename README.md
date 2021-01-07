# PC-Resources

A collection of resources for Program Committee chairs.

## [Scripts for Managing a PC meeting over Zoom](PC-meeting-scripts/)

See the directory [PC-meeting-scripts/](PC-meeting-scripts/).

## [Reviewing guidelines for Program Committee members (for PLDI'16)](https://emeryblogger.com/2018/03/22/reviewing-guidelines-for-program-committee-members/)

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


