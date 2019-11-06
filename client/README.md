# datamaster


Uploading
---------

**Client needs (create)**

- Alert server to new data set.
- Get path to store it in (with creds).
- Perform the storage call. So client must support this (can open more connections ect).
- Alert server on state of the upload.

**Server needs (create)**

- Store that you have a new instance. To support recovery, we should have a "history" type storage in addition to the rolled-up current state.
- Get a path for it
- Send path with SAS to client so upload can start.

** Client needs (sync) **
- Get list of new files stored. Probably want a sequential "records since last time" kind of idea here. Or just dump the db for short.

** Server needs (sync) **
- Send list of new files stored.

**Client data**

- Creds - where to store them? how does git do this?
- Server to contact.

