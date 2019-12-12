=================================
Getting Started with Data Master
=================================
Mind your data without losing your Mind
------------------------------------------


After reading this document, you will have created your first data set with DM.

**What is DataMaster?**
DM is a tool to deal with data sets so you can focus on algorithms. 
It lets you deal with data sets as objects not raw files. 
Data objects can:

- Be versioned, both by setting a branch like git and by storing 
  different outputs for different configurations of your program.
- Be shared with other users (and among your scripts) 
  without worrying about the mechanics of sharing raw files.

Our goal in building DM is maximal efficiency with minimal overhead. So let's get started!

**Make your first data set**

The following python program creates a file and stores some data

.. code:: python

    import json 
    my_data = json.dumps([{'id': 1, 'age': 33'}])
    fh = open("/tmp/ages.json", "w")
    fh.write(my_data)
    fh.close()

Let's modify this program to use DM to manage the output:

.. code:: python

    import json 
    from dm import out
    my_data = json.dumps([{'id': 1, 'age': 33'}])
    fh = open(out.ages, "w")
    fh.write(my_data)
    fh.close()

The snippet ``out.ages`` creates a data set called "ages" (we'll
discuss namespacing soon) and creates a filename for python to open.

If you hate surprises (I do!) and don't fully trust magic 
(I don't) then this section should dispel that 
concern. Here's what really 
happened when we used ``out.ages``.

First, DM recorded a new dataset called ``ages``. You can put that
dataset in a project, which we'll cover later. This dataset will 
record information about your file. Your file is still there, but
it's stored in a cache folder owned by DM. You can see it here:

.. code-block:: bash

    >> ls /tmp/dm/
    ages
    >> cat /tmp/dm/ages
    [{'id': 1, 'age': 33'}]


**Read your data**

To read your file, you can reference it just like you did when
it was created:

.. code-block:: python

    from dm import input
    print(open(input.ages, 'r').read())

DataMaster figures out where ``ages`` is stored and passes the correct file to python.

TODO - tab complete

**Controlling the output with additional data**

Machine Learning Scientists and other data folks frequently train models
with different input data sets and/or different meta parameters. 

For instance, say I write a program to train a DNN, and I train the 
model with three different values for the parameter ``lr``. 

.. code-block:: python

    lrs = [1e-5, 2e-5, 3e-5]
    for lr in lrs:
        model = train_my_model(lr)
        model.save("/tmp/model.pt")

If I want to save all three models, what filenames should I use? 
DM handles that for you:

.. code-block:: python

    from dm import out

    lrs = [1e-5, 2e-5, 3e-5]
    for lr in lrs:
        model = train_my_model(lr)
        model.save(out.model(metaargs={'lr': lr}))

In this case, DM saved three different files: one file for every unique metaargs value.

When you refer back to these three files, you can access them by the value of their metaargs:

.. code-block:: python

    from dm import input

    model = pytorch.load(input.model(metaargs={'lr': 1e-5}))
    model.eval()
    ...

Sometimes, you may want to make sure the file has a particular extension. 
You can do that by augmenting the dataset:

.. code-block:: python

    from dm import out
    fh = open(out.model(format='pt'))

While DM still controls where the file goes, we will append ".pt".

**Listing different versions**


docstring

list command

**Branching**
