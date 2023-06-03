# Overview

All parts of this project can be run through main.py. Running `main.py -h` in a terminal will show the help information.
Specific commands used are described below.

# Indexing

NOTE: I had my datasets inside a data folder with no extra directory layers.
ie: mainDirectory/data/developer_dataset/<domain folders>

To index the analyst dataset:
`python main.py --index -d test -op -b none`

To index the developer dataset:
`python main.py --index -d large -op -b none`

The index will be created inside a new folder "index". If both indexes are to be created, the first one must be renamed
before the second one is created.
(I used makeIndexes.bat to run both commands easily.)

# Running a Query Through the terminal

To start the terminal interface:
`python main.py --query -i <indexFolder>`
eg: `python main.py --query -i indexLarge`

This will start the engine and repeatedly prompt the user for a query. Enter a query and press enter to search.
Hit the Enter key without entering a query to exit.

# Running the Search Interface

Run `python run.py`.
After a second, this will open the search interface in your default browser. Enter a query into the search bar
and either click the search button or press Enter to search.

Press CTRL+C in the terminal to stop the server.

# Refactoring the Index

My index can work on any arbitrary number of breakpoints. The index is split on the breakpoints into multiple files,
eg: on breakpoints ["a", "i", "r"], the index is split into 4 files, split by term lexicographically compared with the breakpoints.
My recent indexes used no breakpoints, but until just after Milestone 2 I was using them to achieve faster results (this later became
irrelevant to query speed). Regardless, the refactoring code still exists.

To refactor an index, run:
`python main.py --refactor -i <indexFolder> -b <breakpoints>`
The breakpoints can be entered as a list, eg: `-b a i r`, or a special option used.
There are 4 special options for refactoring breakpoints: "long" (63 files), "mid" (37 files), "short" (10 files), and "none" (1 file).