#include "DHT.h"

#define DHTPIN  4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(DHTPIN, INPUT_PULLUP);
  dht.begin();
  Serial.println("Capteur DHT11 pret !");
}

void loop() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("Erreur : lecture DHT22 echouee !");
    delay(20000);
    return;
  }

  Serial.print("Temperature : ");
  Serial.print(temp);
  Serial.println(" C");

  Serial.print("Humidite    : ");
  Serial.print(hum);
  Serial.println(" %");

  Serial.println("---");
  delay(20000);
}