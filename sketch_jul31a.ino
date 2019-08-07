#include <ESP8266WiFi.h>
#include <Wire.h>
#include <PubSubClient.h>

#define wifi_ssid "Redmi"
#define wifi_password "Codeblack@123"

#define mqtt_server "192.168.43.121"
//#define mqtt_server "0.0.0.0"
#define mqtt_user ""
#define mqtt_password ""

#define humidity_topic "sensor/humidity"
#define temperature_topic "sensor/temperature"

WiFiClient espClient;
PubSubClient client(espClient);
//Adafruit_HDC1000 hdc = Adafruit_HDC1000();

const int trigPin = 12;
const int echoPin = 13;
long duration;
float distanceCm, distanceInch;

void setup() {
  // Sensor pin set to input and output
  delay(10);
  // WiFi setup
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  // Set SDA and SDL ports
  Wire.begin(2, 14);
    Serial.println("before pin");
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
    Serial.println("after pin");
}

void setup_wifi() {
  // Connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(wifi_ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(wifi_ssid, wifi_password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    // If you do not want to use a username and password, change next line to
    // if (client.connect("ESP8266Client")) {
    if (client.connect("ESP8266Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

long sensor_operation() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);  
  duration = pulseIn(echoPin, HIGH);
  Serial.println(String(duration).c_str());
  return duration;
}

long lastMsg = 0;
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  float d = sensor_operation();
  distanceCm = d*0.034/2;
  distanceInch = d*0.0133/2;
  
 // if (now - lastMsg > 1000) {
    lastMsg = now;
    Serial.print("Distance (in cm):");
    Serial.println(String(distanceCm).c_str());
    client.publish(temperature_topic, String(distanceCm).c_str(), true);
    Serial.print("Distance (in In):");
    Serial.println(String(distanceInch).c_str());
    client.publish(humidity_topic, String(distanceInch).c_str(), true);
    delay(1000);
  //}
}
