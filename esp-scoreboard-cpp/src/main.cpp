/**
 * mosquitto_pub -h 127.0.0.1 -t esp-8266-in/blah -m $'blahxx\x11blah'
 * mosquitto_sub -v -h localhost -t 'esp-8266-out/#'
 * 
 */
#include "Arduino.h"
#include "constants.h"
#include "ESP8266WiFi.h"
#include "PubSubClient.h"
// #include "NTPClient.h"
// #include "WiFiUdp.h"
// #include "certificate.h"
#include <PCA9685.h>

WiFiClient wifiClient;
// WiFiUDP ntpUDP;
// NTPClient timeClient(ntpUDP);
PubSubClient mqttClient(wifiClient);


const char* mqttTopicIn = "esp-8266-in/#";
const char* mqttTopicOut = "esp-8266-out";

PCA9685* boards[10];
int nBoards=0;
unsigned char currSegments[10*2];
int brightness=800;

// Set LED_BUILTIN if it is not defined by Arduino framework
// #define LED_BUILTIN 13

void callback(const char* topic, byte* payload, unsigned int payloadLen) {
  static bool toggle=0;
  static char buffer[100];
  String info = "";

  digitalWrite(LED_BUILTIN, toggle=!toggle);

  Serial.print("Message arrived on topic: '");
  Serial.print(topic);
  Serial.printf("' with payload[%d]: ", payloadLen);
  for (unsigned int i = 0; i < payloadLen; i++) {
     Serial.print((char)payload[i]);
  }
  Serial.println();
  const char *subtopic=topic+strlen(mqttTopicIn)-1 /* -1 wegen #*/ ;
  char *spayload=buffer;
  Serial.printf("subtopic: %s\n", subtopic);
  if(payloadLen >= sizeof(buffer) ) {
    info="payload too long";
    goto error;
  }
  strncpy(spayload, (const char*) payload, payloadLen);
  if(strcmp(subtopic, "init")==0) {  // payload=0x63,0x64, ...\0
    Serial.printf("init: payload len=%d\n", payloadLen);
    digitalWrite(12, 1);
    nBoards=0;
    for(unsigned int i = 0; i < payloadLen; i++) {
      int boardAddr=payload[i];
      Serial.printf("init board[%d] @%d\n", nBoards, boardAddr);
      if(boards[nBoards]) delete(boards[nBoards]);
      boards[nBoards]=new PCA9685(boardAddr);
      boards[nBoards]->setFrequency(1000);

      nBoards++;
      if(nBoards >= 10) {
        info="too many boards";
        goto error;
      }
    }
    /*
    char *pos=spayload;
    char *laststart=pos;
    while(*pos) {
      if(*pos==',') {
        *pos='\0';
        nBoards=0;
        char *endptr=NULL;
        int boardAddr=strtol(laststart, &endptr,0);
      }
    }
    */
  } else if(strcmp(subtopic, "setbrightness")==0) {
    brightness=atol(spayload);
    Serial.printf("set brightness=%d\n", brightness);
  } else if(strcmp(subtopic, "set")==0) {
    if((signed) payloadLen > nBoards*2) {
      info="string too long";
      goto error;
    }
    Serial.printf("set: payload len=%d\n", payloadLen);
    for(unsigned int i = 0; i < payloadLen; i++) {
      if(payload[i] != currSegments[i]) {
        int boardNr=i/2;
        int ab=i%2;
        for(int b = 0; b < 8; b++) {
          Serial.printf("   segment[%d:%d]=>%d\n", boardNr, b+ab*8, currSegments[i] & (1 << b) ? brightness : 0);
          if((payload[i] & (1 << b)) != (currSegments[i] & (1 << b))) {
            Serial.printf("set segment[%d:%d]=%d\n", boardNr, b+ab*8, currSegments[i] & (1 << b) ? brightness : 0);
            boards[boardNr]->setPWM(b+(ab*8), currSegments[i] & (1 << b) ? brightness : 0);
          }
        }
        currSegments[i]=payload[i];
      }
    }
  } else {
    info="invalid toic";
    goto error;
  }

   
//    String myCurrentTime = timeClient.getFormattedTime();
  mqttClient.publish(mqttTopicOut,("ok: " + info).c_str());
  return;
error:
  mqttClient.publish(mqttTopicOut,("error: " + info).c_str());
}

void setup_wifi() {

  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }





  Serial.println("WiFi connected");
}


void setup()
{
  // initialize LED digital pin as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(15, OUTPUT);
  Serial.begin(75400);
  Serial.print("setup()\n");

  setup_wifi();
  mqttClient.setServer(mqtt_server, mqtt_server_port);
  mqttClient.setCallback(callback);
}

//--------------------------------------
// function connect called to (re)connect
// to the broker
//--------------------------------------
void connect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    String mqttClientId = "";
    if (mqttClient.connect(mqttClientId.c_str(), mqttUser, mqttPassword, mqttTopicOut, 2, false, "disconnected")) {
//     if (mqttClient.connect(mqttClientId.c_str())) {
      Serial.println("connected");
      mqttClient.subscribe(mqttTopicIn);
      mqttClient.publish(mqttTopicOut,"connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" will try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop()
{
//  Serial.printf("loop\n");
  if (!mqttClient.connected()) {
     connect();
  }
  mqttClient.loop();

/*
  // turn the LED on (HIGH is the voltage level)
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(12, HIGH);

  // wait for a second
  delay(1000);

  // turn the LED off by making the voltage LOW
  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(12, LOW);
   // wait for a second
  delay(1000);
*/
}
