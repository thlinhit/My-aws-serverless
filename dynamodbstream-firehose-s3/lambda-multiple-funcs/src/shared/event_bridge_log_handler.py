import json
from typing import List

import boto3

event_bridge_client = boto3.client("events")

def send_to_event_bus(records) -> bool:
    print(records)
    # entries = []
    # for record in records:
    #     if record.record.find('ACTIMIZE_429') != -1:
    #         detail = {
    #             'status': 'RETRYABLE',
    #             'payload': record.record
    #         }
    #         entry = {
    #             'Source': 'com.tyme.actimize.ifm.egress.log-extension',
    #             'DetailType': 'ACTIMIZE_DATA_EVENT',
    #             'Detail': json.dumps(detail),
    #             'EventBusName': 'tp-actimize-bus'
    #         }
    #         get_logger().debug(f"entry {entry}")
    #         entries.append(entry)
    #     else:
    #         get_logger().debug(f"skip log {record.record}")
    # if len(entries) > 0:
    #     response = event_bridge_client.put_events(Entries=entries)
    #     get_logger().debug(f"EventBridgeHandler handle {response}")
