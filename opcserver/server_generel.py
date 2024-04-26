import sys
import asyncio

sys.path.insert(0, "..")
import time
import math
import logging
import datetime
import random

# from opcua import ua, Server
from asyncua import ua, Server

LEVEL_0 = "Power Site Frankfurt East"  # "Maschinenbau"
DEVICE_0 = "Transformer Type III"  # "Maschinen Type III"
DEVICE_1 = "Controller"  # "Drives"
DEVICE_2 = "LV Winding"  # "Spindel"
DEVICE_3 = "Radiator"  # "Wechseltisch"
DEVICE_4 = "Conservator"  # "Controller"
LEVEL_1 = "Site"  # "Werk"
LEVEL_2 = "Power Station"  # "Halle"
LEVEL_3 = "Power Sub-Station"  # "Linie"
LEVEL_4 = "Transformer"  # "Machine 0815"
LEVEL_4 = "Transformer"  # "Machine 0815"


async def main():
    logger = logging.getLogger("Server")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Logger for Server was initialized")

    # setup our server
    logger.info("Starting Server")
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/server")
    server.set_server_name("Power Example OPCUA Server")

    # set all possible endpoint policies for clients to connect through
    server.set_security_policy(
        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ]
    )
    # setup our own namespace, not really necessary but should as spec
    uri = "http://power_generation_operator.freeopcua.io"
    idx = await server.register_namespace(uri)

    # create object type & object
    mycustomobj_type = await server.nodes.base_object_type.add_object_type(idx, "Transformer_Type_III")
    await (await mycustomobj_type.add_variable(0, "power_variable", 220.0)).set_modelling_rule(
        True
    )  # if false it would not be instantiated
    myproperty = await mycustomobj_type.add_property(idx, "device_id", "123456")
    await myproperty.set_modelling_rule(True)

    # First a folder to organise our nodes
    my_level_0 = await server.nodes.objects.add_folder(idx, LEVEL_0)
    my_device_0_level_0 = await my_level_0.add_object(idx, DEVICE_0, mycustomobj_type.nodeid)
    my_detailed_level_1 = await my_level_0.add_folder(idx, f"{LEVEL_1}-2")  # werk
    await my_level_0.add_folder(idx, f"{LEVEL_1}-1")
    await my_level_0.add_folder(idx, f"{LEVEL_1}-3")
    my_level_2_3 = f"{LEVEL_2}-3"
    my_level_2 = await my_detailed_level_1.add_folder(idx, my_level_2_3)
    my_level_3 = await my_level_2.add_folder(idx, f"{LEVEL_3}-4")
    my_device_0_level_3 = await my_level_3.add_folder(idx, LEVEL_4)
    my_device_0_level_4 = await my_device_0_level_3.add_object(idx, DEVICE_1)
    my_device_1_level_4 = await my_device_0_level_3.add_object(idx, DEVICE_2)
    my_device_2_level_4 = await my_device_0_level_3.add_object(idx, DEVICE_3)
    power = await my_device_0_level_4.add_variable(idx, "Power", 6.7)
    amplitude = await my_device_0_level_4.add_variable(idx, "Amplitude", 20.0)
    current = await my_device_0_level_4.add_variable(idx, "Current", 6.7)
    resolution = await my_device_0_level_4.add_variable(idx, "Resolution", 100)
    await power.set_writable()  # Set MyVariable to be writable by clients
    await current.set_writable()
    await resolution.set_writable()
    await amplitude.set_writable()
    my_device_3_level_4 = await my_device_0_level_3.add_object(idx, DEVICE_4)
    await my_device_3_level_4.set_modelling_rule(True)
    # state = ctrl.add_property(idx, "State", "Idle")
    state = await my_device_3_level_4.add_variable(idx, "State", "idle")
    await state.set_writable()
    await state.set_modelling_rule(True)


    # enable data change history for this particular node, must be called after start since it uses subscription
    # await server.historize_node_data_change(power, period=None, count=100)
    
    # creating a default event object
    # The event object automatically will have members for all events properties
    # you probably want to create a custom event type, see other examples
    myevgen = await server.get_event_generator()
    myevgen.event.Severity = 300

    # starting!
    async with server:
        try:
            # enable following if you want to subscribe to nodes on server side
            # handler = SubHandler()
            # sub = await server.create_subscription(500, handler)
            # handle = await sub.subscribe_data_change(myvar)
            i = 0
            logger.info("Starting loop")
            frequency = await resolution.get_value()
            await state.set_value("active")
            while True:
                i = i + 1
                # time.sleep(0.5)
                await asyncio.sleep(1.0)
                seconds = time.time()
                simPower = (await amplitude.get_value()) * abs(math.sin(seconds * frequency / 100))
                await current.set_value(round(math.cos(seconds) * 10.0, 2))
                frequency = frequency + 0.05 * frequency * random.randint(
                    -1, 1
                )  # Step direction (-1, 0, +1)
                await power.set_value(round(simPower, 2))
                if i <= 20:
                    await state.set_value("idle")
                elif i <= 40:
                    await state.set_value("active")
                elif i < 150:
                    await state.set_value("maintenance")
                elif i >= 150:
                    i = 0
                simState = await state.get_value()
                logger.info(
                    "Power: " + str(round(simPower, 2)) + " Status: " + str(simState)
                )
        finally:
            # close connection, remove subcsriptions, etc
            server.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # optional: setup logging
    # logger = logging.getLogger("asyncua.address_space")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.internal_server")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.binary_server_asyncio")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.uaprocessor")
    # logger.setLevel(logging.DEBUG)

    asyncio.run(main())
