NXSDataWriter project
=====================

Authors: Jan Kotanski, Eugen Wintersberger, Halil Pasic
Introduction

NXSDataWriter is a Tango server which allows to store NeXuS Data in H5 files.

The server provides storing data from other Tango devices, various databases
as well as passed by a user client via JSON strings.


---------------------------
Installation from sources
---------------------------

Install the dependencies:

    pni-libraries, PyTango, numpy

Download the latest NexDaTaS version from

    https://github.com//nexdatas/writer

Extract sources and run

$ python setup.py install

------------------
General overview
------------------

All operations carried out on a beamline are orchestrated by the control client (CC),
a software operated by the beamline-scientist and/or a user. Although the term client
suggests that it is only a minor component aside from all the hardware control servers,
databases, and whatever software is running on a beamline it is responsible for all
the other components and tells them what to do at which point in time. In terms of
an orchestra the CC is the director which tells each group of instruments or individual
artist what to do at a certain point in time.

It is important to understand the role of the CC in the entire software system on a beamline
as it determines who is responsible for certain operations. The CC might be a simple
single script running on the control PC which can is configured by the user before start
or it might be a whole application of its own like SPEC or ONLINE. Historically it is
the job of the CC to write the data recorded during the experiment (this is true at least
for low rate data-sources). However, with the appearance of complex data formats
like Nexus the IO code becomes more complex.

---------------
Project goals
---------------

The aim of this project is to implement a Tango server that manages data IO
for synchrotron (and maybe neutron) beamlines. The server should satisfy the
following requirements

  * remove responsibility for data IO from the beamline control client
  * provide a simple configuration mechanism via NXDL
  * read data from the following sources without client interaction
      # SQL databases (MySQL, Postgres, Oracle, DB2, ...)
      # other TANGO servers
      # JSON records (important for the interaction with the client and SARDANA)
  * the first implementation of the server will be written in Python
  * the communication model of the first implementation will be strictly synchronous
      (future version most probably will support other communication models too)
  * the control client software has full control over the behavior of the server
      via TANGO commands
  * only low data-rate sources will be handled directly by the server. High data-rate
  * sources will write their data independently and additional software will add this data
     to the Nexus file produced by the server once the experiment is finished.

The server should make it easy to implement control clients which write Nexus files
as the entire Nexus logic is kept in the server. Clients only produce NXDL configurations
or use third party tools for this job. The first Python implementation of
this server will serve as a proof of concept.



NXDL extensions
===============

In order to describe various data sources the NXDL standard has been extended by XML tags listed
below. Thus, <strategy /> and <datasource /> can be situated inside <field/> or <attribute/> tags.
The other ones are nested inside <datasource/> tag.

------------------
The <strategy> tag
------------------

The **strategy** tag defines when and in which way the data is stored.

An example of usage:

.. code-block:: xml
		
   <field name="energy" type="NX_FLOAT" units="GeV" >
     <strategy mode="STEP" trigger="trigger1" />
     <datasource type="CLIENT">
      <record name="counter_1"/>
     </datasource>
   </field>

The tag can have the following attributes:
  + **mode** specifies when the data is fetched, i.e.
      - *INIT* during opening a new entry
      - *STEP* when the record() command is performed
      - *FINAL* at the time of closing the entry
      - *POSTRUN* during post-processing stage
  + **trigger** stands for the name of the related trigger in asynchronous STEP mode (optional)
  + **grows** selects which a field dimension grows of in the STEP mode. The default growing
            dimension is the first one, i.e. grows=1 (optional)
  + **compression** specifies if data is compressed (optional)
      - *true* data going to be compressed
      - *false* data stored without compression (default)
  + **rate** compression rate (optional)
      - from 0 to 9
  + **shuffle** compression shuffle (optional)
      - true shuffle enabled (default)
      - false shuffle disabled
  + **canfail** specifies if during reading data exception should be thrown (optional)
      - false on error exception is raised (default)
      - true on error warning info is printed and the record is filled by a maximum value
             for the record type

The **content** of the strategy tags is an label describing data merged into the H5 file by
a post-processing program.

Another example of usage:

.. code-block:: xml

   <field name="energy" type="NX_FLOAT" units="GeV" >
     <strategy mode="POSTRUN" >
       http://haso.desy.de:/data/energy.dat
     </strategy>
   </field>


The <datasource> tag
--------------------

The **datasource** tag specifies a type of the used data sources. They can be one of built types,
i.e. CLIENT, TANGO, DB, PYEVAL or external ones -- defined in external python package
and registered via JSON data.

The <datasouce> tag acquires the following attributes:

  + **type** related to a type of data source with possible values:
      - *CLIENT* for communication with client via JSON strings
      - *TANGO* for taking data from Tango servers
      - *DB* for fetching data from databases
      - *PYEVAL* for evaluating data from other data sources by python script
      - *other type name* of data source which has been registered via JSON data.
  + **name** datasource name (optional)

CLIENT datasource
--------------------

The **CLIENT** datasource allows to read data from client JSON strings. It should contain
a <record /> tag. An example of usage:

.. code-block:: xml
		
   <datasource type="CLIENT" name="exp_c01">
     <record name="counter_1"/>
   </datasource>


<record>
++++++++

The **record** tag defines the fetched data by its name. It has an attrbute

  + **name** which for the CLIENT data source type denotes a name of the data in the JSON string

An example of usage:

.. code-block:: xml
		
   <record name="Position"/>

TANGO datasource
--------------------

The **TANGO** datasource allows to read data from other TANGO devices. It should contain <device/>
and <record/> tags. An example of usage:

.. code-block:: xml
		
   <datasource type="TANGO">
     <device hostname="haso.desy.de" member="attribute" name="p09/motor/exp.01"
             port="10000" encoding="LIMA_VIDEO_IMAGE"/>
     <record name="Position"/>
   </datasource>

<device>
++++++++   

The **device** tag describes the Tango device which is used to get the data.
It has the following attributes:

  + **name** corresponding to a name of the Tango device
  + **member** defining a type of the class member, i.e.
      - *attribute* an attribute to read
      - *command* a result of a command to take
      - *property* a property to read
  + **hostname** a name of the host with the Tango device server (optional)
  + **port** a port number related to the Tango device server (optional)
  + **encoding** a label defining a required decoder for DevEncoded? data (optional)
  + *group* tango group name (optional)

If group attribute is defined data of the same group is read simultaneously and
only ones during one experimental step.

<record>
++++++++

The **record** tag defines the fetched data by its name. It has an attrbute

  + **name** which for the TANGO data source type a name of the tango class member

DB datasource
-------------

The *DB* datasource allows to read data from accessible databases. It should contain <database />
and <query> tags. An example of usage:

.. code-block:: xml
		
   <datasource type="DB">
     <database dbname="tango" dbtype="MYSQL" hostname="haso.desy.de"/>
     <query format="SPECTRUM">
       SELECT pid FROM device limit 10
     </query>
   </datasource>

<database>
++++++++++   

The **database** tag specifies parameters to connect to the required database. It acquires
the attirbutes

  + **dbtype** describing a type of the database, i.e.
      - *ORACLE* an ORACLE database
      - *MYSQL* a MySQL database
      - *PGSQL* a PostgreSQL database
  + **dbname** denoting a name of the database (optional)
  + **hostname** being a name of the host with the database (optional)
  + **port** corresponding to a port number related to the database (optional)
  + **user** denoting a user name (optional)
  + **passwd** being a user password (optional)
  + **mycnf** defining a location of the my.cnf file with MySQL database access configuration (optional)
  + **node** corresponding to a node parameter for the ORACLE database(optional)

The **content** of the database tag defines Oracle DSN string (optional)

<query>
+++++++

The **query** tag defines the database query which fetches the data. It has one attribute

  + **format** which specifies a dimension of the fetch data, i.e.
      - *SCALAR* corresponds to 0-dimensional data, e.g. a separate numerical value or string
      - *SPECTRUM* is related to 1-dimensional data, e.g. a list of numerical values or strings
      - *IMAGE* describes 2-dimensional data, i.e. a table of specific type values,
                e.g. a table of strings

The **content** of the query tags is the SQL query.
Another example of usage:

.. code-block:: xml
		
   <datasource type="DB">
     <database dbname="mydb" dbtype="PGSQL"/>
     <query format="IMAGE">
       SELECT * FROM weather limit 3
     </query>
   </datasource>



PYEVAL datasource
-----------------

The **PYEVAL** datasource allows to read data from other datasources and evaluate it
by user python script. An example of usage:

.. code-block:: xml
		
   <datasource type="PYEVAL">
     <datasource type="TANGO" name="position">
       <device hostname="haso.desy.de" member="attribute" name="p09/motor/exp.01" port="10000"/>
       <record name="Position"/>
     </datasource>
     <datasource type="CLIENT" name="shift">
       <record name="exp_c01"/>
     </datasource>
     <result name="finalposition">
       ds.finalposition = ds.position + ds.shift
     </result>
   </datasource>


<datasource>
++++++++++++

The **PYEVAL** datasource can contain other datasources. They have to have defined **name** attributes.
Those names with additional prefix 'ds.' correspond to input variable names from the python script,
i.e. ds.name.

<result>
++++++++

The **result** contains python script which evaluates input data. It has the following attribute:

  + **name** corresponding to a result name. It is related to python script variable by ds.name.

The default value **name** ="result". (optional)

--------------------
Client code
--------------------

In order to use Nexus Data Server one has to write a client code. Some simple client codes
are in the  nexdatas repository. In this section we add some
comments related to the client code.

.. code-block:: python

   # To use the Tango Server we must import the PyTango module and create DeviceProxy for the server.

   import PyTango

   device = "p09/tdw/r228"
   dpx = PyTango.DeviceProxy(device)
   dpx.set_timeout_millis(10000)

   dpx.Init()

   # Here device corresponds to a name of our Nexus Data Server. Init() method resets the state of the
   # server.

   dpx.FileName = "test.h5"
   dpx.OpenFile()

   # We set the name of the output HDF5 file and open it.

   # Now we are ready to pass the XML settings describing a structure of the output file as well as
   # defining a way of data storing. Examples of the XMLSettings can be found in the XMLExamples
   # directory.

   xml = open("test.xml", 'r').read()
   dpx.XMLSettings = xml

   dpx.JSONRecord = '{"data": {"parameterA":0.2},
			 "decoders":{"DESY2D":"desydecoders.desy2Ddec.desy2d"},
			 "datasources":{"MCLIENT":"sources.DataSources.LocalClientSource"}
			}'

   dpx.OpenEntry()

   # We read our XML settings settings from a file and pass them to the server via the XMLSettings
   # attribute. Then we open an entry group related to the XML configuration. Optionally, we can also
   # set JSONRecord, i.e. an attribute which contains a global JSON string with data needed to store
   # during opening the entry and also other stages of recording. If external decoder for DevEncoded?
   # data is need one can registred it passing its packages and class names in JSONRecord,
   #  e.g. "desy2d" class of "DESY2D" label in "desydecoders.desy2Ddec" package.
   # Similarly making use of "datasources" records of the JSON string one can registred additional
   # datasources. The OpenEntry method stores data defined in the XML string with strategy=INIT.
   # The JSONRecord attribute can be changed during recording our data.

   # After finalization of the configuration process we can start recording the main experiment
   #  data in a STEP mode.

   dpx.Record('{"data": {"p09/counter/exp.01":0.1, "p09/counter/exp.02":1.1}}')

   # Every time we call the Record method all nexus fields defined with strategy=STEP are
   # extended by one record unit and the assigned to them data is stored. As the method argument
   # we pass a local JSON string with the client data. To record the client data one can also use
   # the global JSONRecord string. Contrary to the global JSON string the local one is only
   # valid during one record step.

   dpx.Record('{"data": {"emittance_x": 0.1},  "triggers":["trigger1", "trigger2"]  }')

   # If you denote in your XML configuration string some fields by additional trigger attributes
   # you may ask the server to store your data only in specific record steps. This can be helpful
   # if you want to store your data in asynchronous mode. To this end you define in
   # the local JSON string a list of triggers which are used in the current record step.

   dpx.JSONRecord = '{"data": {"parameterB":0.3}}'
   dpx.CloseEntry()

   # After scanning experiment data in 'STEP' mode we close the entry. To this end we call
   # the CloseEntry method which also stores data defined with strategy=FINAL. Since our HDF5 file
   # can contains many entries we can again open the entry and repeat our record procedure. If we
   # define more than one entry in one XML setting string the defined entries are recorded parallel
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
