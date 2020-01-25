=================================
Working with DataMaster remotes
=================================
Share your work!
------------------------------------------

DataMaster supports collaboration by allowing you to sync your local data 
with a team project. The core idea to share data is the DataMaster **remote**. 
This document covers a few details about creating and managing remotes.

**Create a remote**

To create a remote, use the ``remote add`` function like so:

.. code-block:: bash

    >> dmaster remote add <remote name> <host>

``dmaster`` will prompt your for your username and password. For instance, this 
command will make a local remote called ``origin``:

.. code-block:: bash

    >> dmaster remote add origin https://datamasterstage.azurewebsites.net/
    Username for https://datamasterstage.azurewebsites.net: 
    Enter password for https://datamasterstage.azurewebsites.net:
    Saved remote https://datamasterstage.azurewebsites.net as origin and set to active. You should log in with 'sync'.


TODO - cover editing a remote
cover removing a remote
if you have many teams, resyncing will make sure they are all available.
