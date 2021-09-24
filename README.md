# OPC Server and Gateway

This solution creates a sample OPCServer including the required gateway to connect the OPC server to Cumulocity.
See as well: [OPC UA Agent Cumulocity](https://cumulocity.com/guides/10.7.0-beta/protocol-integration/opcua)
The registration data are stored in the ./data directory that are mapped as a volume to the docker service gateway. And thus still exits after a restart

# Edit docker-compose.yaml and adapt the baseUrl,identifier and the tenantId:
    version: "3.9"
    services:
    opcserver:
        build:
        context: ./opcserver
        ports:
        - "4840:4840"
    gateway:
        build:
        context: ./gateway
        environment:
        - baseURL=https://TENANT_URL
        - tenantId=TENANT_ID
        - identifier=GATEWAY_IDENTIFIER
        volumes:
        - ./data/:/data

The start the solution by running:

    docker-compose up -d --no-deps --build

# Register opcserver with: opc.tcp://opcserver:4840

![Register OPC server](./doc/Register.png)

# Browse OPC tree

Once the gateway scanned the OPCTree you can view its content:

![Browse OPC tree](./doc/OPC_Tree.png)

_____________________
This widget is provided as-is and without warranty or support. They do not constitute part of the Software AG product suite. Users are free to use, fork and modify them, subject to the license agreement. While Software AG welcomes contributions, we cannot guarantee to include every contribution in the master pro
