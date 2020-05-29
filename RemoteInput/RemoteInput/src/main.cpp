#include <Arduino.h>
#include <map>
#include <IRremoteESP8266.h>
#include <IRrecv.h>
#include <IRutils.h>
#include <setup.h>
#include <elegoo.h>
#include <ircontroller.h>

IRrecv irrecv(RECV_PIN);
decode_results result;

void setup()
{
  Serial.begin(115200);
  Serial.println("Initialized");
  pinMode(RECV_PIN, INPUT);
  irrecv.enableIRIn();
}

void loop()
{
  if (FALSE == irrecv.decode(&result))
  {
    return;
  }

  Serial.print("Code 0x");
  serialPrintUint64(result.value, HEX);
  irrecv.resume();
  Serial.println();
  delay(100);
}