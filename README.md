# Containerized Secure Tunneling Component for Greengrass V2

For details on the AWS IoT Secure Tunneling, please refer to [the
documentation](https://docs.aws.amazon.com/iot/latest/developerguide/secure-tunneling.html).

This Greengrass V2 component provides the
[aws-iot-device-client](https://github.com/awslabs/aws-iot-device-client) and a
Python application packaged into a container image. The Python app watches for
new tunnel notification and spawn off an `aws-iot-device-client´ with the
correct tokens on your Greengrass device to connect securely via the AWS Cloud.

The Python app in this component subscribes to the AWS IoT Core MQTT message
broker on the `$aws/things/greengrass-core-device/tunnels/notify` topic to
receive new incoming secure tunneling notifications. The access tokens are then
passed to the `aws-iot-device-client` and not stored or persisted anywhere else.

This component is deploying a single Docker container running in "host network
mode". This allows new connections directly passed through to the Greengrass
host system. Currently the only supported service for tunneling is SSH on
tcp/22. This port does not need to be exposed to the public internet, but needs
to accept incoming connections from localhost. If your Greengrass device is
using a different network architecture, please adapt the Docker commands in the
`recipe.yaml` file accordingly.

Using a container to deploy this component provides flexibility and portability
without needing to install [dependencies and
requirements](https://docs.aws.amazon.com/greengrass/v2/developerguide/secure-tunneling-component.html#secure-tunneling-component-requirements)
of the `aws-iot-device-client` into the host system. Specifically, OpenSSL
(libcrypto or libssl) and Python 3 dependencies are all included in matching
versions. This also provides a flexible way of using different or non-standard
Linux distributions on the Greengrass host, which are not yet supported by
either the official Greengrass Secure Tunneling component, or the
`aws-iot-device-client`. You can build and deploy this container for your
processor architecture by using the included `Dockerfile` and the GDK build
script. The container image is uploaded to your S3 bucket, and the Greengrass
device needs read access to retrieve it during deployment of the component.

A helper script to open a fresh tunnel and start the
[localproxy](https://github.com/aws-samples/aws-iot-securetunneling-localproxy)
on your local system is included, also running in a portable container.

More information at:

* https://docs.aws.amazon.com/greengrass/v2/developerguide/secure-tunneling-component.html
* https://github.com/awslabs/aws-iot-device-client
* https://docs.aws.amazon.com/iot/latest/developerguide/local-proxy.html
* https://github.com/aws-samples/aws-iot-securetunneling-localproxy

## Comparison to `aws.greengrass.SecureTunneling` Component

The [AWS-provided Secure tunneling
component](https://docs.aws.amazon.com/greengrass/v2/developerguide/secure-tunneling-component.html)
is a related, but different, approach to the one presented in this repository.
The Containerized Secure Tunneling Component, in this repository, uses a
container image to package all dependencies and abstract operating system and
Linux distribution differences away, so that customers can deploy one container
image to different devices with different and possibly unsupported operating
systems. The only dependency is the Docker application manager, part of
Greengrass. The AWS-provided Secure tunneling component requires libraries and
other packages to be installed in the operating system before deploying the
component. Only some Linux distributions are supported out-of-the-box, while the
containerized variant (in this repository) can be deployed to any system with a
Docker container runtime. Using the Dockerfile and script files in this
repository, customers can further customize this component and use it a
blueprint for their own version.

## Deployment

You can deploy this component with the provided Greengrass component recipe file
`recipe.yaml`. There are no configuration options for the component.

You can build and publish the container image with
[GDK](https://github.com/aws-greengrass/aws-greengrass-gdk-cli), see the
`gdk-config.json` for more details. Using GDK, the container will be built using
the provided `build-custom.sh` script and then uploaded to an S3 bucket of your
choice.

Commands to build and publish using GDK:

* gdk component build
* gdk component publish

## Usage

First, build and publish the component into your AWS account.

Second, deploy the component to your Greengrass devices.

Third, on your local computer, use the `get-ssh.sh` script to create a new
Secure Tunnel and open a local proxy to it. This requires the Docker image of
local-proxy and Docker running on your local computer, see the script for
detailed instructions:

```bash
$ ./get-ssh.sh MyTestThing
Secure Tunnel created with tunnelId: a6f53db4-6a65-4cc9-b24c-800442b166d8.
[2021-12-01T12:01:00]{1}[info]    Starting proxy in source mode
[2021-12-01T12:01:00]{1}[info]    Attempting to establish web socket connection with endpoint wss://data.tunneling.iot.eu-central-1.amazonaws.com:443
[2021-12-01T12:01:00]{1}[info]    Web socket session ID: 5faba3b5-93a9-41e3-adeb-eebf9fa69125
[2021-12-01T12:01:00]{1}[info]    Successfully established websocket connection with proxy server: wss://data.tunneling.iot.eu-central-1.amazonaws.com:443
[2021-12-01T12:01:00]{1}[info]    Updated port mapping for v1 format: 
[2021-12-01T12:01:00]{1}[info]    SSH = 22
[2021-12-01T12:01:00]{1}[info]    Listening for new connection on port 22
<...>
[2021-12-01T12:01:23]{1}[info]    Accepted tcp connection on port 22 from 172.17.0.1:54321
<...> CTRL-C
Secure Tunnel a6f53db4-6a65-4cc9-b24c-800442b166d8 closed.
```

Finally, connect from your local computer to the Greengrass device via local
proxy using any of your usual SSH utilities. Use `127.0.0.1:2222` and a Linux
user from your Greengrass host to establish a secure connection:

```bash
$ ssh greengrassdevice@127.0.0.1 -p 2222
greengrassdevice@ip-172-31-10-200:~$ 
<... live interactive shell now available ...>
```

## Logging

You can view the logs of the Greengrass component under
`/greengrass/v2/logs/aws.greengrass.labs.CustomSecureTunneling.log` on your Greengrass
device. A successfully deployed and started component looks like this:

```
2022-03-16T12:00:00.000Z [WARN] (pool-2-thread-40) aws.greengrass.labs.CustomSecureTunneling: Command ["docker run \\n      --rm \\n      --name=secure_tunneling \\n      --network=host..."] did not respond to interruption within timeout. Going to kill it now. {serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=STOPPING}
2022-03-16T12:00:00.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: Run script exited. {exitCode=137, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=NEW}
2022-03-16T12:00:00.000Z [INFO] (pool-2-thread-42) aws.greengrass.labs.CustomSecureTunneling: shell-runner-start. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Install.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=NEW, command=["docker load -i /greengrass/v2/packages/artifacts/aws.greengrass.labs.CustomSec..."]}
2022-03-16T12:00:01.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. Loaded image: greengrass_custom_secure_tunneling:NEXT_PATCH. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Install.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=NEW}
2022-03-16T12:00:01.000Z [INFO] (pool-2-thread-42) aws.greengrass.labs.CustomSecureTunneling: shell-runner-start. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=STARTING, command=["docker run \\n  --name=greengrass_custom_secure_tunneling \\n  --network=host \\n..."]}
2022-03-16T12:00:01.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. Starting Greengrass Secure Tunneling notification watcher.... {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:01.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. Subscribed to $aws/things/Demo-Thing/tunnels/notify. Waiting for notifications.... {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
<...>
```

Once a new tunnel is created, the `aws-iot-device-client` is configured and
startup up, you will see these log entries about the:
```
<...>
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. New tunnel event received.... {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. Starting aws-iot-device-client.... {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. /app/aws-iot-device-client --enable-tunneling true --tunneling-region eu-central-1 --tunneling-service SSH --endpoint data.tunneling.iot.eu-central-1.amazonaws.com --tunneling-disable-notification --config-file dummy_config.json --log-level DEBUG. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [WARN]  {FileUtils.cpp}: Permissions to given file/dir path './' is not set to recommended value... {Permissions: {desired: 745, actual: 755}}. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [INFO]  {Config.cpp}: Successfully fetched JSON config file: {. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. "endpoint": "replace_with_endpoint_value>",. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. "cert": "replace_with_certificate_file_path",. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. "key": "replace_with_private_key_file_path",. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. "root-ca": "replace_with_root_ca_file_path",. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. "thing-name": "replace_with_thing_name_replace_with_client_id". {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. }. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [DEBUG] {Config.cpp}: Did not find a runtime configuration file, assuming Fleet Provisioning has not run for this device. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [INFO]  {Main.cpp}: Now running AWS IoT Device Client version v1.0.89. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [INFO]  {SharedCrtResourceManager.cpp}: SDK logging is disabled. Enable it with --enable-sdk-logging on the command line or logging::enable-sdk-logging in your configuration file. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [INFO]  {Main.cpp}: Secure Tunneling is enabled. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [INFO]  {SecureTunneling.cpp}: Running Secure Tunneling!. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [INFO]  {Main.cpp}: Client base has been notified that Secure Tunneling has started. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:00:02.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:00:02.000Z [DEBUG] {SecureTunnelingContext.cpp}: SecureTunnelingContext::OnConnectionComplete. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
<...>
```

Once we are done with SSH session and close the tunnel, the `aws-iot-device-client` will be stopped:
```
<...>
2022-03-16T12:01:33.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:01:33.000Z [DEBUG] {SecureTunnelingContext.cpp}: SecureTunnelingContext::OnConnectionShutdown. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:01:33.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:01:33.000Z [DEBUG] {SecureTunneling.cpp}: SecureTunnelingFeature::OnConnectionShutdown. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:01:33.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:01:33.000Z [INFO]  {Main.cpp}: Secure Tunneling has stopped. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
2022-03-16T12:01:33.000Z [INFO] (Copier) aws.greengrass.labs.CustomSecureTunneling: stdout. 2022-03-16T12:01:33.000Z [INFO]  {Main.cpp}: All features have stopped. {scriptName=services.aws.greengrass.labs.CustomSecureTunneling.lifecycle.Run.Script, serviceName=aws.greengrass.labs.CustomSecureTunneling, currentState=RUNNING}
<...>
```

## Testing using pytest

Make sure you have the following packages installed:

```bash
pip3 install pytest pytest-mock pytest-cov awsiotsdk
```

Then run the following to get coverage tests on the backend application that will run on the device:

```bash
pytest --cov=src --cov-report=term-missing
```

## Security
See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more
information.

## License
This library is licensed under the MIT-0 License. See the LICENSE file.
