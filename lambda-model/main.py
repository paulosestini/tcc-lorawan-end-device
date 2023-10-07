import numpy as np
import pickle
import base64
import textwrap
import pymysql.cursors
import dotenv
import os
import json
from datetime import datetime

dotenv.load_dotenv()

db_connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    passwd=os.getenv("DB_PWD"),
    user=os.getenv("DB_USER"),
    database=os.getenv("DB_NAME"),
)

label_map = {0: "background", 1: "person", 2: "car", 3: "dog", 4: "cow"}

n_features = 25

def build_float16(float_in_int):
    float16_value = np.frombuffer(
        float_in_int.to_bytes(2, byteorder="little"), dtype=np.float16
    )[0]
    return float16_value


def read_packet(packet):
    packet = base64.b64decode(packet)
    if len(packet) < 2 * n_features:
        return None
    features_high = map(lambda x: x << 8, packet[:n_features])
    features_low = packet[n_features:]

    features = list(map(sum, zip(features_high, features_low)))

    packet = list(map(build_float16, features))

    return np.array(packet)


def lambda_handler(event, context):
    #event = {"body": build_body_mock()}
    body = json.loads(event["body"])
    print('Event body: ', body)
    model_input = read_packet(body["data"])
    print('Model input: ', model_input)
    if model_input is None:
        return {'statusCode': 200, 'body': 'Received Packet'}
    
    model_input = model_input.reshape(1, -1)

    pickle_file = open("knn_pickle", "rb")
    model = pickle.load(pickle_file)
    pickle_file.close()

    pred = model.predict(model_input)
    pred = label_map[pred[0]]

    save_event(dev_id=body["deviceInfo"]["devEui"], timestamp=body["time"], label=pred)

    return {'statusCode': 200, 'body': 'Received CSI Features'}


def save_event(dev_id, timestamp, label):
    with db_connection.cursor() as cursor:
        cursor.execute(
            f"""
                insert into events(dev_id, ts, label)
                values ('{dev_id}', '{timestamp}', '{label}');
            """
        )
    db_connection.commit()


def build_body_mock():
    high_bits = "01000111"
    low_bits = "11100111"
    sample_packet = (
        high_bits * n_features
        + low_bits * n_features
    )
    packet_bytes = list(map(lambda x: int(x, 2), textwrap.wrap(sample_packet, 8)))
    packet_bytes = bytearray(packet_bytes)
    sample_packet = base64.b64encode(packet_bytes)

    body_mock = {
        "deduplicationId": "bf344cae-f6d4-43f7-a340-b243f551c56a",
        "time": f"{datetime.utcnow().isoformat()}+00:00",
        "deviceInfo": {
            "tenantId": "52f14cd4-c6f1-4fbd-8f87-4025e1d49242",
            "tenantName": "ChirpStack",
            "applicationId": "889b0d7f-7c34-4d28-8fff-19356b92c051",
            "applicationName": "Bliu",
            "deviceProfileId": "9c0778d3-fa26-4c24-92d5-50d31de4a99f",
            "deviceProfileName": "Default",
            "deviceName": "Default",
            "devEui": "ab64e4da0ac1ca3f",
            "deviceClassEnabled": "CLASS_A",
            "tags": {},
        },
        "devAddr": "33333333",
        "adr": True,
        "dr": 5,
        "fCnt": 54153,
        "fPort": 1,
        "confirmed": True,
        "data": f"{sample_packet}",
        "rxInfo": [
            {
                "gatewayId": "909b639e5d477c02",
                "uplinkId": 27471,
                "rssi": -77,
                "snr": 10.0,
                "channel": 4,
                "rfChain": 1,
                "location": {},
                "context": "raHo8w==",
                "metadata": {
                    "region_config_id": "au915_0",
                    "region_common_name": "AU915",
                },
                "crcStatus": "CRC_OK",
            }
        ],
        "txInfo": {
            "frequency": 916000000,
            "modulation": {
                "lora": {
                    "bandwidth": 125000,
                    "spreadingFactor": 7,
                    "codeRate": "CR_4_5",
                }
            },
        },
    }

    return body_mock


if __name__ == "__main__":
    print(lambda_handler(None, None))
    #packet=(read_packet("3b3b3b3b3b3232323b32323b3b3b3b3b323b3b323b3b33323b7f5a75616d260b244f1416597f899e4001aa981e4a8e0d1b46"))
    #print(packet)