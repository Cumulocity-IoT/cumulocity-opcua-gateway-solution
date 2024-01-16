import sys
sys.path.insert(0, "..")
import time
import math
import logging
import datetime
import random

from opcua import ua, Server

LEVEL_0 = "Power Site Frankfurt East"     # "Maschinenbau"
DEVICE_0 = "Transformer Type III"         # "Maschinen Type III"
DEVICE_1 = "Controller"                   # "Drives"
DEVICE_2 = "LV Winding"                   # "Spindel"
DEVICE_3 = "Radiator"                     # "Wechseltisch"
DEVICE_4 = "Conservator"                  # "Controller"
LEVEL_1 = "Site"                          # "Werk"
LEVEL_2 = "Power Station"                 # "Halle"
LEVEL_3 = "Power Sub-Station"             # "Linie"
LEVEL_4 = "Transformer"                   # "Machine 0815"
LEVEL_4 = "Transformer"                   # "Machine 0815"

if __name__ == "__main__":
    logger = logging.getLogger('Server')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info('Logger for Server was initialised')

    # setup our server
    logger.info('Starting Server')
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/server")
    server.set_server_name("Power Example OPCUA Server")

    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
    # setup our own namespace, not really necessary but should as spec
    uri = "http://power_generation_operator.freeopcua.io"
    idx = server.register_namespace(uri)

    objects = server.get_objects_node()

    # get Objects node, this is where we should put our nodes
    types = server.get_node(ua.ObjectIds.BaseObjectType)
    object_type_to_derive_from = server.get_root_node().get_child(["0:Types", 
                                                                   "0:ObjectTypes", 
                                                                   "0:BaseObjectType"])
    # create object type & object
    mycustomobj_type = types.add_object_type(idx, "Transformer_Type_III")
    mycustomobj_type.add_variable(0, "power_variable", 220.0).set_modelling_rule(True) #if false it would not be instantiated
    mycustomobj_type.add_property(idx, "device_id", "123456").set_modelling_rule(True)


     # First a folder to organise our nodes
    my_level_0 = server.nodes.objects.add_folder(idx, LEVEL_0)
    my_device_0_level_0 = my_level_0.add_object(idx, DEVICE_0, mycustomobj_type.nodeid)
    my_detailed_level_1 = my_level_0.add_folder(idx, f"{LEVEL_1}-2") # werk
    my_level_0.add_folder(idx, f"{LEVEL_1}-1")
    my_level_0.add_folder(idx, f"{LEVEL_1}-3")
    my_level_2_3 = f"{LEVEL_2}-3"
    my_level_2 = my_detailed_level_1.add_folder(idx, my_level_2_3)
    my_level_3= my_level_2.add_folder(idx, f"{LEVEL_3}-4")
    my_device_0_level_3= my_level_3.add_folder(idx, LEVEL_4)
    my_device_0_level_4 = my_device_0_level_3.add_object(idx, DEVICE_1)
    my_device_1_level_4 = my_device_0_level_3.add_object(idx, DEVICE_2)
    my_device_2_level_4 = my_device_0_level_3.add_object(idx, DEVICE_3)
    power=  my_device_0_level_4.add_variable(idx, "Power", 6.7)
    amplitude =  my_device_0_level_4.add_variable(idx, "Amplitude", 20.0)
    current = my_device_0_level_4.add_variable(idx, "Current", 6.7)
    resolution = my_device_0_level_4.add_variable(idx, "Resolution", 100)
    power.set_writable()    # Set MyVariable to be writable by clients
    current.set_writable()
    resolution.set_writable()
    amplitude.set_writable()
    my_device_3_level_4 = my_device_0_level_3.add_object(idx, DEVICE_4)
    my_device_3_level_4.set_modelling_rule(True)
    # state = ctrl.add_property(idx, "State", "Idle")
    state = my_device_3_level_4.add_variable(idx, "State", "idle")
    state.set_writable()
    state.set_modelling_rule(True)

    # starting!
    server.start()

    # enable data change history for this particular node, must be called after start since it uses subscription
    server.historize_node_data_change(power, period=None, count=100)
    try:
        i = 0
        logger.info('Starting loop')
        frequency = resolution.get_value()
        state.set_value("active")
        while True:
            i = i + 1
            # time.sleep(0.5)
            time.sleep(10.0)
            seconds = time.time()
            simPower = amplitude.get_value() * abs( math.sin(seconds * frequency / 100) )
            current.set_value( round(math.cos(seconds) * 10.0, 2))
            frequency = frequency + 0.05 * frequency * random.randint(- 1,1 )   # Step direction (-1, 0, +1)
            power.set_value(round(simPower,2))
            if ( i <= 20 ):
                state.set_value("idle")
            elif ( i <= 40 ):
                state.set_value("active")
            elif ( i < 150 ):
                state.set_value("maintenance")
            elif ( i >= 150 ):
                i = 0
            simState = state.get_value()
            logger.info('Power: ' + str(round(simPower,2)) + ' Status: ' + str(simState))
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
