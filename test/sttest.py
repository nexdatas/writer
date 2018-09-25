import PyTango
import subprocess
import time
import sys

new_device_info_writer = PyTango.DbDevInfo()
new_device_info_writer._class = "SimpleServer"
new_device_info_writer.server = "SimpleServer/S1"
new_device_info_writer.name = "stestp09/testss/s1r228"

db = PyTango.Database()
db.add_device(new_device_info_writer)
db.add_server(new_device_info_writer.server, new_device_info_writer)

# time.sleep(1)

psub = subprocess.Popen(
    "./ST S1 &", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
# psub = os.system("./ST S1 &")
# time.sleep(0.3)

# time.sleep(10)


try:
    #  dp = PyTango.DeviceProxy(new_device_info_writer.name)

    found = False
    cnt = 0
    while not found and cnt < 100000:
        try:
            sys.stdout.write("\b.")
            dp = PyTango.DeviceProxy(new_device_info_writer.name)
            time.sleep(0.0001)
        #       print "STATE:",dp.state()
            if dp.state() == PyTango.DevState.ON:
                found = True
        except Exception as e:
            print("WHAT: %s" % e)
            found = False
            cnt += 1
    print("STATE: %s" % dp.state())


finally:
    print("tearing down ...")
    db = PyTango.Database()
    db.delete_server(new_device_info_writer.server)
    output = ""
    pipe = subprocess.Popen(
        "ps -ef | grep 'SimpleServer.py S1'", stdout=subprocess.PIPE,
        shell=True).stdout

    res = pipe.read().split("\n")
    for r in res:
        sr = r.split()
        if len(sr) > 2:
            subprocess.call("kill -9 %s" %
                            sr[1], stderr=subprocess.PIPE, shell=True)
