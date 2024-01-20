from src.shared.event_bridge_log_handler import send_to_event_bus


def handler(event, context):
    send_to_event_bus(event)
    # print(event)