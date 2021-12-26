
from datetime import datetime
import time
import traceback
import json
import boto3
import botocore
import sys
import os
import picamera

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    SubscribeToIoTCoreRequest,
    PublishToIoTCoreRequest
)
import Adafruit_DHT as dht

# Setup some constants and pull command line args and environment variables.
TIMEOUT = 10
BUCKET = sys.argv[1]
REQUEST_TOPIC = sys.argv[2]
RESPONSE_TOPIC = sys.argv[3]
THING_NAME = os.getenv('AWS_IOT_THING_NAME', 'unknown')
TEMP_PIC = '/tmp/snap.jpg'
SENSOR_GPIO = 26

ipc_client = awsiot.greengrasscoreipc.connect()


def take_picture():
    # Initiate the PiCam and try to snap a photo.  Note that you will get an error if you happen to access the PiCam from two places at once
    # such as if there is a new thread started for this program.  I have only run into it when one Python thread got stuck, but we could implement
    # some single-file queing if it becomes an issue.
    try:
        camera = picamera.PiCamera()
        time.sleep(2)
        camera.capture(TEMP_PIC)
        picture_result = "success"
    except Exception as e:
        print(e)
        picture_result = "failed"
    finally:
        camera.close()
        return picture_result


def get_temp():
    h, t = dht.read_retry(dht.DHT22, SENSOR_GPIO)
    return(round(t, 1), round(h, 1))


def respond(event):
    # This is the main response function when we notice a message on the request topic.
    picture_result = take_picture()
    if picture_result == "failed":
        image_url = "Unable to get picture"
    elif picture_result == "success":
        image_url = upload_file(BUCKET, TEMP_PIC)

    # Get the temp and humidity from the sensor
    t, h = get_temp()

    response_message = {
        "timestamp": int(round(time.time() * 1000)),
        "image": image_url,
        "temperature": "{} C".format(t),
        "humidity": "{}%".format(h)
    }

    # Using the AWS IOT SDK to publish messages directly to AWS.  Using QOS=1 (AT_LEAST_ONCE) to have Greengrass queue up
    # the messages if we happen to loose internet connectivity...which happens with the LTE modem
    response = PublishToIoTCoreRequest()
    response.topic_name = RESPONSE_TOPIC
    response.payload = bytes(json.dumps(response_message), "utf-8")
    response.qos = QOS.AT_LEAST_ONCE
    response_op = ipc_client.new_publish_to_iot_core()
    response_op.activate(response)


def upload_file(bucket, pic_filepath):
    # Upload the file to S3.  Note that I'm setting a PUBLIC-READ ACL just for ease of troubleshooting.
    # You probably would not want to do this unless it's truly a public endeavour.
    try:
        s3_client = boto3.client('s3')
        filename = RESPONSE_TOPIC + '/' + THING_NAME + '/' + \
            str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.jpg'
        s3_client.upload_file(pic_filepath, bucket, filename,
                              ExtraArgs={'ACL': 'public-read'})
        url = 'https://{}.s3.amazonaws.com/{}'.format(BUCKET, filename)

    except botocore.exceptions.ClientError as e:
        url = e.response

    finally:
        return url


class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    # Setup a class to do stuff upon topic activity.
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            respond(event)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass


# Setup the MQTT Subscription
request = SubscribeToIoTCoreRequest()
request.topic_name = REQUEST_TOPIC
request.qos = QOS.AT_LEAST_ONCE
handler = StreamHandler()
operation = ipc_client.new_subscribe_to_iot_core(handler)
future = operation.activate(request)
future.result(TIMEOUT)

# Keep the main thread alive, or the process will exit.
while True:
    time.sleep(10)

# To stop subscribing, close the operation stream.
operation.close()
