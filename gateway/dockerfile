### 1. Get Linux
FROM alpine:3.8

### 2. Get Java via the package manager
RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk8-jre


####
#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it

#ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

####

ADD application-tenant.yaml /
ADD logging.xml /
ADD http://resources.cumulocity.com/examples/opc-ua/opcua-device-gateway-1007.0.23.jar /

CMD ["/usr/bin/java", "-Dlogging.config=file:./logging.xml", "-Dspring.profiles.active=default,tenant", "-jar", "opcua-device-gateway-1007.0.23.jar", "-Dspring.config.location=file:./application-tenant.yaml"]