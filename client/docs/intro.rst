=================================
Getting Started with Data Master
=================================
Mind your data without losing your Mind
------------------------------------------


After reading this document, you will have created your first data set with DM.

**What is DataMaster?**
DM is a tool to deal with data sets so you can focus on algorithms. 
It lets you created and manipulate data sets as objects not raw files. 
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
    from dm import outputs
    my_data = json.dumps([{'id': 1, 'age': 33'}])
    fh = open(outputs.ages, "w")
    fh.write(my_data)
    fh.close()

The snippet ``outputs.ages`` creates a data set called "ages" (we'll
discuss namespacing soon) and creates a filename for python to open.

If you hate surprises (I do!) and don't fully trust magic 
(I don't) then this section should dispel that 
concern. Here's what really 
happened when we used ``outputs.ages``.

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

    from dm import outputs

    lrs = [1e-5, 2e-5, 3e-5]
    for lr in lrs:
        model = train_my_model(lr)
        model.save(outputs.model(metaargs={'lr': lr}))

In this case, DM saved three different files: one file for every unique metaargs value.

When you refer back to these three files, you can access them by the value of their metaargs:

.. code-block:: python

    from dm import inputs

    model = pytorch.load(inputs.model(metaargs={'lr': 1e-5}))
    model.eval()
    ...

Sometimes, you may want to make sure the file has a particular extension. 
You can do that by augmenting the dataset:

.. code-block:: python

    from dm import outputs
    fh = open(outputs.model(extension='pt'))

While DM still controls where the file goes, we will append ".pt".

**Data with time ranges**

.. code-block:: python

Many data sets have a partition scheme based on date or other factors. Datamaster supports writing to partition schemes. You can write to partitions two few ways, all of which result in the same thing to DataMaster:

1) Explicitly add partition information using plus:

    from dm import outputs
    data = 'this is my data'
    open(outputs.myproject.dailydata + 'year=2022/month=12/day=25', 'w').write()

2) Let an external system handle it:

    from dm import outputs
    from pyarrow import parquet

    data = '' # data with a partition key
    pq.write_to_dataset(table, root_path=str(outputs.myproject.dailydata(meta=meta_args)), partition_cols=['p'])


**Everything else we save: data metadata**

Every dataset creates a metadata folder that tracks everything we can think of for the environment where you read. Specifics we track are:

* machine and user info
* data that was read (if it was read with datamaster!)
* loaded modules and their versions
* python version
* git info including latest commit, branch, and a diff showing any changes.

Our goal is for this data to list everything you would need to comply with model/data provenance regulations.

Here's an example:


    {
        "branch": "master",
        "context": {
            "calling_filename": "C:\\Users\\riguy\\code\\datamaster\\client\\sample_filewrite.py",
            "git_root": {
            "git_active_branch": "datamodel",
            "git_commit_author": {
                "email": "riguy@microsoft.com",
                "name": "Tommy Guy"
            },
            "git_commit_authored_datetime": "2022-07-25 15:21:29-07:00",
            "git_commit_hexsha": "e0fbed609dac786ab91486adad7a188d53acfa1e",
            "git_diff": "diff --git a/client/sample_filewrite.py b/client/sample_filewrite.py\nindex ca68f30..27a19e6 100644\n--- a/client/sample_filewrite.py\n+++ b/client/sample_filewrite.py\n@@ -12,8 +12,8 @@ f.write(\"[]\")\n f.close()\n \n # Write a file as part of a project\n-# This should be written to root/myproject/output1.txt\n-f = open(outputs.myproject.outputone, 'w')\n+# This should be written to root/myproject/outputone.txt\n+f = open(outputs.myproject.outputone(extension='.txt'), 'w')\n f.write(\"projectoutput\")\n f.close()\n ",
            "git_root": "C:\\Users\\riguy\\code\\datamaster",
            "git_untracked": {
                "client/dm/test.txt": "hi there"
            }
            },
            "loaded_modules": {
            "certifi": "2020.6.20",
            "chardet": "3.0.4",
            "gitdb": "4.0.7",
            "idna": "2.10",
            "requests": "2.24.0",
            "smmap": "4.0.0",
            "urllib3": "1.25.9"
            },
            "localmachine": "RIGUYLAPPY4",
            "localusername": "riguy",
            "previousfilereads": [],
            "python_version": "3.8.3 (default, Jul  2 2020, 17:30:36) [MSC v.1916 64 bit (AMD64)]"
        },
        "data_path": "C:\\Users\\riguy\\.datamaster\\data\\master\\myproject\\outputone..txt",
        "dataset_name": "outputone",
        "project": "myproject",
        "writeable_file_data": {
            "file_suffix": ".txt",
            "passed_metadata": {},
            "time_path": null
        }
    }

**Discovering your data**

DM does everything it can to help you discover data sets locally.
Tab complete works as expected.

.. code-block:: python

    >>> from dm import inputs
    >>> inputs. [tab]
    inputs.bar(      inputs.foo(      inputs.myproject inputs.withtime

Docstrings work as expected:

    >>> from dm import inputs
    >>> ?inputs.myproject
    Type:        ReadableProject
    String form: Project myproject
    File:        [omitted]\datamaster\client\dm\readablefile.py
    Docstring:
    Datamaster Project myproject

    Files:
    outputone
    outputtwo
    Projects:
    innerproject

    >>> ?inputs.myproject.weights
    In [5]: ?inputs.withtime.model
    Signature:   inputs.myproject.model(extension=None, meta=None, timepath='')
    Type:        ReadableFileName
    String form: Dataset myproject.model at ~\.datamaster\data\master\withtime\model\2019\11\04\model
    File:        [omitted]\datamaster\client\dm\readablefile.py
    Docstring:
    DataSet stored at ~\.datamaster\data\master\withtime\model\2019\11\04\model

    Branch: master



In addition, you can list datasets with the command line utility:

.. code-block:: bash

    $ dm list
    <todo>

You can call `dm list` with a dataset name to see full details:

.. code-block:: bash

    $ dm list example
    <todo>


While autocomplete works already from Jupyter, integration with VSCode and PyCharm is coming.



**Organizing your work**

**Projects**



**Branching**

explain that it's useful for keeping some work local if/when we do merge upstream.
