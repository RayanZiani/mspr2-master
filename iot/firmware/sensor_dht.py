import dht
import machine


class SensorDHT22:
    def __init__(self, pin: int = 4):
        self._sensor = dht.DHT22(machine.Pin(pin))

    def read(self) -> dict:
        self._sensor.measure()
        return {
            "temp": self._sensor.temperature(),
            "humidity": self._sensor.humidity(),
        }
