### Managing a PC meeting over Zoom.

These scripts were written by Breanna Devore-McDonald and Nicolas van Kempen.

First steps:

1. Collect information about time availability via Doodle; save as "Doodle_availability.csv".

Example of desired format of Doodle time blocks:

    ,November 2020,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    ,Tue 17,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Wed 18,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
    ,6:00 AM – 6:30 AM,6:30 AM – 7:00 AM,7:00 AM – 7:30 AM,7:30 AM – 8:00 AM,8:00 AM – 8:30 AM,8:30 AM – 9:00 AM,9:00 AM – 9:30 AM,9:30 AM – 10:00 AM,10:00 AM – 10:30 AM,10:30 AM – 11:00 AM,11:00 AM – 11:30 AM,11:30 AM – 12:00 PM,12:00 PM – 12:30 PM,12:30 PM – 1:00 PM,1:00 PM – 1:30 PM,1:30 PM – 2:00 PM,2:00 PM – 2:30 PM,2:30 PM – 3:00 PM,3:00 PM – 3:30 PM,3:30 PM – 4:00 PM,4:00 PM – 4:30 PM,4:30 PM – 5:00 PM,5:00 PM – 5:30 PM,5:30 PM – 6:00 PM,6:00 PM – 6:30 PM,6:30 PM – 7:00 PM,7:00 PM – 7:30 PM,7:30 PM – 8:00 PM,8:00 PM – 8:30 PM,8:30 PM – 9:00 PM,9:00 PM – 9:30 PM,9:30 PM – 10:00 PM,10:00 PM – 10:30 PM,10:30 PM – 11:00 PM,6:00 AM – 6:30 AM,6:30 AM – 7:00 AM,7:00 AM – 7:30 AM,7:30 AM – 8:00 AM,8:00 AM – 8:30 AM,8:30 AM – 9:00 AM,9:00 AM – 9:30 AM,9:30 AM – 10:00 AM,10:00 AM – 10:30 AM,10:30 AM – 11:00 AM,11:00 AM – 11:30 AM,11:30 AM – 12:00 PM,12:00 PM – 12:30 PM,12:30 PM – 1:00 PM,1:00 PM – 1:30 PM,1:30 PM – 2:00 PM,2:00 PM – 2:30 PM,2:30 PM – 3:00 PM,3:00 PM – 3:30 PM,3:30 PM – 4:00 PM,4:00 PM – 4:30 PM,4:30 PM – 5:00 PM,5:00 PM – 5:30 PM,5:30 PM – 6:00 PM,6:00 PM – 6:30 PM,6:30 PM – 7:00 PM,7:00 PM – 7:30 PM,7:30 PM – 8:00 PM,8:00 PM – 8:30 PM,8:30 PM – 9:00 PM,9:00 PM – 9:30 PM,9:30 PM – 10:00 PM,10:00 PM – 10:30 PM,10:30 PM – 11:00 PM


2. Save from HotCRP the following files:
   * `yourconfname-conflicts.csv` -- save as `conflicts.csv`
   * `emails.csv` -- only the heavy PC members (that is, those attending the PC meeting)
     - **NOTE**: this was modified by hand to match the Zoom email addresses and exact names, which is important!
   * `heavypc-assignments.csv` -- the paper assignments of the heavy PC members (as above)

3. Set the list of papers that will be discussed:
  * `papers.txt` -- format is one paper number per line
  
## Scripts

* `PC_windows.py`: generates availability windows for each co-chair (currently you need to edit these directly).
* `PC_conflict_finder.py`: lists the papers for which each co-chair is conflicted (as above, edit directly).
* `PC_discussion_windows.py`: generates discussion windows for each paper, taking availability and conflicts into account.
  - outputs a csv in the following format:
    * `paper_number time1_hour time1_min time1_day ... timeN_hour timeN_min timeN_day`
    * see comments in the script for more details
* `PC_discussion_assignment.py`: generates discussion windows for each paper. Imports the following files, which are redirected output from the above scripts:
  - `pc_avail.txt` -- output of `PC_windows.py`
  - `times.txt` -- output of `PC_discussion_windows.py`

To prepare for the Zoom meeting (generating breakout room `.csv` files for each paper), see the directory `zoom_configurations_generation`.
