import os
import sys
import time
import json
import traceback
import subprocess

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    QOS,
    IoTCoreMessage,
    SubscribeToIoTCoreRequest,
)


class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            print("New tunnel event received...")
            message_string = str(event.message.payload, "utf-8")
            msg = json.loads(message_string)
        except:
            print("ERROR: invalid tunnel event payload:", event.message.payload, file=sys.stderr)
            traceback.print_exc()
            return

        for required_fields in ("region", "services", "clientAccessToken"):
            if required_fields not in msg:
                print(f"ERROR: incomplete tunnel event: missing {required_fields}", file=sys.stderr)
                return

        try:
            new_environ = os.environ.copy()
            new_environ["AWSIOT_TUNNEL_ACCESS_TOKEN"] = msg["clientAccessToken"]

            config = "dummy_config.json"
            with open(config, "w") as f:
                # no need to fill in any values, the file only needs to exists and have all required keys
                f.write("""{
                    "endpoint": "not_needed_see_argv",
                    "cert": "not_needed_see_argv",
                    "key": "not_needed_see_argv",
                    "root-ca": "not_needed_see_argv",
                    "thing-name": "not_needed_see_argv"
                }""")

            cmd = [
                "/app/aws-iot-device-client",
                "--enable-tunneling", "true",
                "--tunneling-region", msg["region"],
                "--tunneling-service", msg["services"][0],
                "--endpoint", f"data.tunneling.iot.{msg['region']}.amazonaws.com",
                "--tunneling-disable-notification",
                "--config-file", config,
                "--log-level", "DEBUG",
            ]
            print(f"Starting aws-iot-device-client...")
            print("    ", " ".join(cmd))

            subprocess.Popen(cmd, env=new_environ, start_new_session=True, stderr=subprocess.STDOUT)
        except:
            print("ERROR: failed to configure and start aws-iot-device-client", file=sys.stderr)
            traceback.print_exc()
            return

    def on_stream_error(self, error: Exception) -> bool: # pragma: nocover
        print("ERROR:", error)
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None: # pragma: nocover
        print("Stream closed.")


def init_watcher():
    print("Starting Greengrass Secure Tunneling notification watcher...")

    if 'AWS_IOT_THING_NAME' not in os.environ:
        print("ERROR: missing AWS_IOT_THING_NAME. Are you running as a GGv2 component?", file=sys.stderr)
        sys.exit(1)

    handler = StreamHandler()
    ipc_client = awsiot.greengrasscoreipc.connect()
    operation = ipc_client.new_subscribe_to_iot_core(handler)

    topic_name = f"$aws/things/{os.environ['AWS_IOT_THING_NAME']}/tunnels/notify"
    request = SubscribeToIoTCoreRequest(topic_name=topic_name, qos=QOS.AT_LEAST_ONCE)
    future = operation.activate(request)
    future.result(15)

    print(f"Subscribed to {request.topic_name}. Waiting for notifications...")


if __name__ == "__main__": # pragma: nocover
    init_watcher()

    while True:
        time.sleep(30)
