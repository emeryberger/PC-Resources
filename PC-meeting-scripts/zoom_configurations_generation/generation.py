import csv
import os

confname = "asplos21"

papers = {} # paper id -> paper title
conflicts = {} # paper id -> List of emails of people with conflicts
participants = [] # [{first, last, hotcrp_mail, zoom_mail}]

# This will generate configurations for ALL paper (not only those not rejected).
# To only generate configurations for non-rejected papers, use the proper CSV files.

# Load papers
with open(confname + "-pcassignments.csv", encoding="utf8") as file:
    skip = True
    for row in csv.reader(file): # Skip header
        if skip:
            skip = not skip
            continue
        id = row[0] # paper id
        if len(row) > 4: # Only three columns on rows with no title.
            papers[id] = row[4]

# Load conflicts
with open(confname + "-pcconflicts.csv", encoding="utf8") as file:
    skip = True
    for row in csv.reader(file): # Skip header
        if skip:
            skip = not skip
            continue
        id = row[0] # paper id
        mail = row[4]
        if id in conflicts:
            conflicts[id].append(mail)
        else:
            conflicts[id] = [mail]

# Load participants
# Updated from https://docs.google.com/spreadsheets/d/11krSOSrNRreq2XTg4u6aQBCdUqsXCePKZxSkr7ETapk
with open(confname + "-participants.csv", encoding="utf-8") as file:
    skip = True
    for row in csv.reader(file): # Skip header
        if skip:
            skip = not skip
            continue
        first = row[0]
        last = row[1]
        hotcrp_mail = row[2]
        zoom_mail = None

        if len(row) > 3 and row[3] == "Y":
            zoom_mail = hotcrp_mail
        elif len(row) > 4 and row[4] != "":
            zoom_mail = row[4]
                    
        if zoom_mail is None:
            # When no Zoom email is specified, print this error message and default to the HotCRP email.
            print("%s %s <%s> did not specify whether their Zoom email was the same as their HotCRP email." % (first, last, hotcrp_mail))
            participants.append({ "first": first, "last": last, "hotcrp_mail": hotcrp_mail, "zoom_mail": hotcrp_mail, "no_zoom_mail_provided": True })
        else:
            participants.append({ "first": first, "last": last, "hotcrp_mail": hotcrp_mail, "zoom_mail": zoom_mail })
        

# Generate configuration files (The `configurations` directory should be deleted before running this script)
os.mkdir("configurations")
for paper_id in papers:
    with open("configurations/configuration_%s.csv" % paper_id, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Pre-assign Room Name", "Email Address"])
        for participant in participants:
            if paper_id in conflicts and participant["hotcrp_mail"] in conflicts[paper_id]:
                writer.writerow(["Conflict Room", participant["zoom_mail"]])
            # If we want to keep the discussion in the main room, these two lines just needs to be commented out.
            # else:
                # writer.writerow(["Discussion (%s)" % paper_id, participant["zoom_mail"]])

# Generate human-readable Markdown file.
with open("configurations/_CONFLICTS.md", "w", encoding="utf-8") as file:
    file.write("# " + confname +" Conflicts\n")
    for paper_id in papers:
        file.write("\n\n## %s (%s)\n\n" % (papers[paper_id], paper_id))
        if paper_id not in conflicts:
            file.write("No conflicts.")
        else:
            written = False
            for participant in participants:
                if participant["hotcrp_mail"] in conflicts[paper_id]:
                    written = True
                    file.write(" -  %s %s <%s> (Zoom: <%s>)\n" % (participant["first"], participant["last"], participant["hotcrp_mail"], "?" if participant.get("no_zoom_mail_provided", False) else participant["zoom_mail"]))
            if not written:
                file.write("No conflicts.\n")
