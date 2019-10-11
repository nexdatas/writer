Welcome to NXSDataWriter's documentation!
=========================================

Authors: Jan Kotanski, Eugen Wintersberger, Halil Pasic

------------
Introduction
------------

NXSDataWriter is a Tango server which allows to store NeXuS Data in H5 files.

The server provides storing data from other Tango devices,
various databases as well as passed by a user client via JSON strings.

Tango Server API: https://nexdatas.github.io/writer/doc_html

| Source code: https://github.com/nexdatas/writer
| Project Web page: https://nexdatas.github.io/writer
| NexDaTaS Web page: https://nexdatas.github.io

------------
Installation
------------

Install the dependencies:

|    pni-libraries, PyTango, numpy

From sources
""""""""""""

Download the latest NexDaTaS version from

|    https://github.com/nexdatas/writer

Extract sources and run

.. code-block:: console

	  $ python setup.py install

Debian packages
"""""""""""""""

Debian Jessie (and Wheezy) packages can be found in the HDRI repository.

To install the debian packages, add the PGP repository key

.. code-block:: console

	  $ sudo su
	  $ wget -q -O - http://repos.pni-hdri.de/debian_repo.pub.gpg | apt-key add -

and then download the corresponding source list

.. code-block:: console

	  $ cd /etc/apt/sources.list.d
	  $ wget http://repos.pni-hdri.de/jessie-pni-hdri.list

Finally,

.. code-block:: console

	  $ apt-get update
	  $ apt-get install python-nxswriter

To instal other NexDaTaS packages

.. code-block:: console

	  $ apt-get install python-nxstools nxsconfigserver-db python-nxsconfigserver nxsconfigtool

and

.. code-block:: console

	  $ apt-get install python-nxsrecselector nxselector python-sardana-nxsrecorder

for Component Selector and Sardana related packages.

From pip
""""""""

To install it from pip you can

.. code-block:: console

   $ python3 -m venv myvenv
   $ . myvenv/bin/activate

   $ pip install nxswriter

Moreover it is also good to install

.. code-block:: console

   $ pip install pytango
   $ pip install pymysqldb
   $ pip install psycopg2-binary
   $ pip install cx-oracle

Setting NeXus Writer Server
"""""""""""""""""""""""""""

To set up  NeXus Writer Server run

.. code-block:: console

          $ nxsetup -x NXSDataWriter

The *nxsetup* command comes from the **python-nxstools** package.

-----------
Client code
-----------

In order to use Nexus Data Server one has to write a client code. Some simple client codes
are in the  nexdatas repository. In this section we add some
comments related to the client code.

.. code-block:: python

   # To use the Tango Server we must import the PyTango module and
   # create DeviceProxy for the server.

   import PyTango

   device = "p09/tdw/r228"
   dpx = PyTango.DeviceProxy(device)
   dpx.set_timeout_millis(10000)

   dpx.Init()

   # Here device corresponds to a name of our Nexus Data Server.
   # The Init() method resets the state of the server.

   dpx.FileName = "test.h5"
   dpx.OpenFile()

   # We set the name of the output HDF5 file and open it.

   # Now we are ready to pass the XML settings describing a structure of
   # the output file as well as defining a way of data storing.
   # Examples of the XMLSettings can be found in the XMLExamples directory.

   xml = open("test.xml", 'r').read()
   dpx.XMLSettings = xml

   dpx.JSONRecord = '{"data": {"parameterA":0.2},
			 "decoders":{"DESY2D":"desydecoders.desy2Ddec.desy2d"},
			 "datasources":{
		              "MCLIENT":"sources.DataSources.LocalClientSource"}
   }'

   dpx.OpenEntry()

   # We read our XML settings settings from a file and pass them to the server via
   # the XMLSettings attribute. Then we open an entry group related to the XML
   # configuration. Optionally, we can also set JSONRecord, i.e. an attribute
   # which contains a global JSON string with data needed to store during opening
   # the entry and also other stages of recording. If external decoder for
   # DevEncoded data is need one can registred it passing its packages and
   # class names in JSONRecord,
   # e.g. "desy2d" class of "DESY2D" label in "desydecoders.desy2Ddec" package.
   # Similarly making use of "datasources" records of the JSON string one can
   # registred additional datasources. The OpenEntry method stores data defined
   # in the XML string with strategy=INIT.
   # The JSONRecord attribute can be changed during recording our data.

   # After finalization of the configuration process we can start recording
   # the main experiment data in a STEP mode.

   dpx.Record('{"data": {"p09/counter/exp.01":0.1, "p09/counter/exp.02":1.1}}')

   # Every time we call the Record method all nexus fields defined with
   # strategy=STEP are extended by one record unit and the assigned to them data
   # is stored. As the method argument we pass a local JSON string with the client
   # data. To record the client data one can also use the global JSONRecord string.
   # Contrary to the global JSON string the local one is only
   # valid during one record step.

   dpx.Record('{"data": {"emittance_x": 0.1},  "triggers":["trigger1", "trigger2"]  }')

   # If you denote in your XML configuration string some fields by additional
   # trigger attributes you may ask the server to store your data only in specific
   # record steps. This can be helpful if you want to store your data in
   # asynchronous mode. To this end you define in the local JSON string a list of
   # triggers which are used in the current record step.

   dpx.JSONRecord = '{"data": {"parameterB":0.3}}'
   dpx.CloseEntry()

   # After scanning experiment data in 'STEP' mode we close the entry.
   # To this end we call the CloseEntry method which also stores data defined
   # with strategy=FINAL. Since our HDF5 file can contain many entries we can again
   # open the entry and repeat our record procedure. If we define more than one entry
   # in one XML setting string the defined entries are recorded parallel
   # with the same steps.

   # Finally, we can close our output file by

   dpx.CloseFile()

Additionally, one can use asynchronous versions of **OpenEntry**, **Record**, **CloseEntry**, i.e.
**OpenEntryAsynch**, **RecordAsynch**, **CloseEntryAsynch**. In this case data is stored
in a background thread and during this writing Tango Data Server has a state *RUNNING*.

In order to build the XML configurations in the easy way the authors of the server provide
for this purpose a specialized GUI tool, Component Designer.
The attached to the server XML examples
was created by XMLFile class defined in XMLCreator/simpleXML.py.
