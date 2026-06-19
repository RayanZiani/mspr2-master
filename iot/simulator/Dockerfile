FROM python:3.11-slim
WORKDIR /app
COPY simulate_sensor.py .
RUN pip install --no-cache-dir paho-mqtt
ENV PAYS=bresil
ENV ENTREPOT=entrepot_A
ENV MQTT_BROKER_HOST=localhost
ENV MQTT_BROKER_PORT=1883
ENV SIMULATE_INTERVAL=30
CMD sh -c "python simulate_sensor.py --pays ${PAYS} --entrepot ${ENTREPOT} --all --interval ${SIMULATE_INTERVAL}"
