import sys
sys.path.insert(0, "..")
import time
import math
import logging
import datetime

from opcua import ua, Server


if __name__ == "__main__":
    logger = logging.getLogger('Server')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info('Logger for Server was initialised')

    # setup our server
    logger.info('Starting Server')
    server = Server()
    logger.info('Setting endpoint')
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    logger.info('Setting Servername')
    server.set_server_name("Maschinenfertiger Example OPCUA Server")

    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    objects = server.get_objects_node()

    # get Objects node, this is where we should put our nodes
    dev = server.nodes.base_object_type.add_object_type(idx, "MyDevice")
    dev.add_variable(idx, "sensor1", 1.0).set_modelling_rule(True)
    dev.add_property(idx, "device_id", "0340").set_modelling_rule(True)

     # First a folder to organise our nodes
    myCompany = server.nodes.objects.add_folder(idx, "Maschinenbau")
    myWerk = myCompany.add_folder(idx, "Werk 2")
    myCompany.add_folder(idx, "Werk 1")
    myCompany.add_folder(idx, "Werk 3")
    myHalle = myWerk.add_folder(idx, "Halle 3")
    myLinie= myHalle.add_folder(idx, "Linie 4")
    myMachine= myLinie.add_folder(idx, "Machine 0815")
    drives = myMachine.add_object(idx, "Drives")
    spindel = myMachine.add_object(idx, "Spindel")
    table = myMachine.add_object(idx, "Wechseltisch")
    power=  drives.add_variable("ns=2;s=Drives/Power", "Power", 6.7)
    amplitude =  drives.add_variable(idx, "Amplitude", 20.0)
    current = drives.add_variable(idx, "Current", 6.7)
    resolution = drives.add_variable(idx, "Resolution", 500)
    power.set_writable()    # Set MyVariable to be writable by clients
    current.set_writable()
    resolution.set_writable()
    amplitude.set_writable()
    ctrl = myMachine.add_object(idx, "Controller")
    ctrl.set_modelling_rule(True)
    ctrl.add_property(idx, "state", "Idle").set_modelling_rule(True)

    # starting!
    server.start()

    # enable data change history for this particular node, must be called after start since it uses subscription
    server.historize_node_data_change(power, period=None, count=100)
    try:
        while True:
            time.sleep(1)
            logger.info('Starting loop')
            seconds = time.time()
            frequency = 100
            logger.info('Frequency is ' + str(frequency))
            logger.info('Calculating power')
            simPower = amplitude.get_value()*math.sin(seconds*frequency/100)
            logger.info('Power is ' + str(simPower))
            logger.info('Changing values on server for resolution')
            resolution.set_value(frequency)
            logger.info('Resolution is now: ' + str(frequency))
            logger.info('Changing values on server for power')
            dv = ua.DataValue(2)
            dv.ServerTimestamp = datetime.datetime.now()
            power.set_value(dv)
            power.set_value(round(simPower,1))
            logger.info('Power is now: ' + str(simPower))
            logger.info('Loop ends, sleeping')
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
