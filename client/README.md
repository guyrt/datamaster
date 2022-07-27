# datamaster

Install Locally
---------------

`python -m pip install -e . --no-build-isolation --no-use-pep517`

Uploading
---------

todo - 
handle many remotes in the same way that you handle many branches - store the active one in a database.

configing settings - you need a default object that will detail where things go. when someone inits a new
workspace, copy those. or ask questions to config it.

test the fallback mechanisms.
- works at root?
- fallback to local?
- no local


need to make a setup.py file and list our dm util

change list util:
- dm list should list the existing datasets and number of files.
- dm list name should list the files/projects in that dataset. have a recursive command

our system works fine for python workflows. how common are those? how would we work with things like direct S3 to S3 workloads?
what do we do with pyspark?

*** - maybe we should keep a "filesystemtype" stamp that tracks differently? ***
