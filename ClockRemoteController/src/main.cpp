#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRrecv.h>
#include <IRutils.h>
#include <elegoo.h>
#include <remoteinput.h>
#include "pins.h"

IRrecv irrecv(IR_RX_PIN);
decode_results results;

void setup()
{
  Serial.begin(115200);
  irrecv.enableIRIn();
}

void loop()
{
  if (irrecv.decode(&results))
  {
    char res = process_remote_input(results.value);
    if (res == (char)0)
    {
      serialPrintUint64(results.value);
      Serial.println();
    }
    else
    {
      Serial.println(res);
    }
    irrecv.resume();
  }
  delay(30);
}