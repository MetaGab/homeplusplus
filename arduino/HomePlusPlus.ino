//Importar las librerías necesarias
#include <SPI.h>
#include <MFRC522.h>
#define RST_PIN         9          
#define SS_PIN          10         
#include "WiFiEsp.h"
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
#include <MQ2.h>
#endif
#include <DHT.h>

//Declaración de los pines a utilizar
const int pirPin =  8;
const int buzzerPin = 7;
const int dhtPin = A1;
const int lightPin = A2;
const int gasPin = A0;
const int dhtType = 11;
const int doorPin = 6;
const int bulbPin = 5;

//Crear objetos de ciertas clases de librerías
SoftwareSerial Serial1(3, 2); 
DHT dht(dhtPin, dhtType);
MQ2 mq2(gasPin);
MFRC522 mfrc522(SS_PIN, RST_PIN);
WiFiEspClient client;

//Definir los valores para la conexión Wifi
char ssid[] = "XXXXX";          
char pass[] = "XXXXX";          
int home_id = 2;
int status = WL_IDLE_STATUS;     
char server[] = "homeplusplus.herokuapp.com";

//Utilizado para las alarmas
bool motionState = false; 
bool alarma = false;
int bulbState = LOW;

//Utilizado para realizar acciones cada cierto tiempo sin parar el programa con delay()
unsigned long time_now = 0;


void setup()
{ 
  //Declaración de modo de pines
  pinMode(pirPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(doorPin, OUTPUT);
  pinMode(bulbPin, OUTPUT);
  digitalWrite(doorPin, LOW);
  digitalWrite(bulbPin, LOW);
  //Inicialización de seriales y de cliente wifi
  Serial.begin(115200);
  Serial1.begin(9600);
  WiFi.init(&Serial1);
  //Inicialización de lectores de librería
  dht.begin();
  mq2.begin();
  SPI.begin();
  mfrc522.PCD_Init();
  //Si el módulo Wifi no se encuentra, no es necesario comenzar el programa
  if (WiFi.status() == WL_NO_SHIELD) {
    while (true);
  }
  // Conexión a red 
  while ( status != WL_CONNECTED) {
    status = WiFi.begin(ssid, pass);
  }
  //Tiempo de inicio despues de setup()
  time_now = millis();
}

void loop()
{
  //Cada minuto el programa hace un ping al servidor web
  if(millis() > time_now + 30000){ 
        //Lectura de humedad (h), temperatura (t), iluminación (l), gas (g)
        int h = dht.readHumidity();
        int t = dht.readTemperature();
        int l = (analogRead(lightPin)-700 ) / 2; //Calibrado tras pruebas en oscuridad/luz
        int g = mq2.readLPG() - 180;
        if (g<0) 
          g=0;
        time_now = millis();
        
        if (client.connect(server, 80)) {
          //Envio de información 
          client.print("GET /info?home=");
          client.print(home_id);
          client.print("&temperature=");
          client.print(t);
          client.print("&humidity=");
          client.print(h);
          client.print("&illumination=");
          client.print(l);
          client.print("&gas=");
          client.print(g);
          client.println(" HTTP/1.1");  
          client.println("Host: homeplusplus.herokuapp.com");
          client.println();
          //Revisa si debe de prender la alarma
          client.print("GET /status_alarma?home=");
          client.print(home_id);
          client.println(" HTTP/1.1");
          client.println("Host: homeplusplus.herokuapp.com");
          client.println();
          if (client.available()) {
            while (client.available()>0){
              char c = client.read();
              if (c == '>'){
                c = client.read();
                if (c=='F'){
                  alarma = false;
                  motionState = false;
                }
                else if (c=='T'){
                  alarma = true;
                }
              }
            }
          }
          //Revisa si debe de prender el foco
          client.print("GET /status_luz?home=");
          client.print(home_id);
          client.println(" HTTP/1.1");
          client.println("Host: homeplusplus.herokuapp.com");
          client.println();
          if (client.available()) {
            while (client.available()>0){
              char c = client.read();
              if (c == '>'){
                c = client.read();
                if (c=='F'){
                  digitalWrite(bulbPin, LOW);
                  bulbState=LOW;
                }
                else if (c=='T'){
                  digitalWrite(bulbPin, HIGH);
                  bulbState = HIGH;
                  if (bulbState==LOW){
                    WiFi.init(&Serial1);
                    status = WiFi.begin(ssid, pass);
                  }
                }
              }
            }
          }
          
          client.stop();
        }
    }
  //Se activa en el caso de que haya lectura de RFID
  if ( mfrc522.PICC_IsNewCardPresent()) {  
      if ( mfrc522.PICC_ReadCardSerial()) 
      {
            byte ActualUID[4];
            //Usuario asociado con la tarjeta
            byte User1[4]= {0x04, 0x24, 0x5C, 0x6A};
            for (byte i = 0; i < 4; i++) { 
                    ActualUID[i]=mfrc522.uid.uidByte[i];          
            }    
            if(compareArray(ActualUID,User1)){
              //Si la tarjeta y el usuario coinciden, apagar alarma y abrir puerta 
              noTone(buzzerPin);
              digitalWrite(doorPin, HIGH);
              delay(3000);
              digitalWrite(doorPin, LOW);
              delay(100);
              //Reiniciar Wifi
              WiFi.init(&Serial1);
              status = WiFi.begin(ssid, pass);
              //Envia el acceso al servidor web
              if (client.connect(server, 80)) {
                client.print("GET /access?home=");
				client.print(home_id);
                client.print("&card=");
                client.print(ActualUID);
                client.println(" HTTP/1.1");
                client.println("Host: homeplusplus.herokuapp.com");
                client.println("Connection: close");
                client.println();
                client.stop();
              }
            }
            mfrc522.PICC_HaltA();
      }
  }
  //Si la alarma esta activada y hay movimiento, activar buzzer, de lo contrario apagar
  if (digitalRead(pirPin) == HIGH && alarma) {
    if (motionState == false) {
      motionState = true;
      tone(buzzerPin, 400);
    }
  }
  else {
    if (motionState == true) {
      motionState = false;
      noTone(buzzerPin);
    }
  }
 
}
//Funcion para comparar arrays de bytes
boolean compareArray(byte array1[],byte array2[])
{
  if(array1[0] != array2[0])return(false);
  if(array1[1] != array2[1])return(false);
  if(array1[2] != array2[2])return(false);
  if(array1[3] != array2[3])return(false);
  return(true);
}
