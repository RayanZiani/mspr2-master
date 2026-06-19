FROM python:3.11-slim
WORKDIR /app
COPY simulate_sensor.py .
RUN pip install --no-cache-dir paho-mqtt
ENV PAYS=bresil
ENV MQTT_BROKER_HOST=localhost
ENV MQTT_BROKER_PORT=1883
ENV SIMULATE_INTERVAL=30
CMD ["python", "simulate_sensor.py"]
