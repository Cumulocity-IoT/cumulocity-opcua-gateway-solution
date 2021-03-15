#Edit application-tenant.yaml and adapt the baseUrl and the tenantId:

    C8Y:
        baseUrl: https://TENANT_URL
    gateway:
        bootstrap:
            tenantId: TENANT_ID
        identifier: Sample_Gateway_Device
        name: Customer Gateway
        db:

The start the solution by running:

    docker-compose up -d --no-deps --build

Register opcserver with: opc.tcp://opcserver:4840

![Register OPC server](../doc/Register.png)