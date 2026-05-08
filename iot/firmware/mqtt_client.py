from umqtt.simple import MQTTClient
import ubinascii
import machine


def get_client(broker: str, port: int) -> MQTTClient:
    client_id = ubinascii.hexlify(machine.unique_id())
    client = MQTTClient(client_id, broker, port=port)
    client.connect()
    return client
