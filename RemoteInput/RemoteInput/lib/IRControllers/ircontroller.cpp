#include "ircontroller.h"

int IrController::process_input(uint64_t ir_input)
{
    switch (ir_input)
    {
    case 0:
        Serial.println("Power Button Pressed");
        break;
    default:
        break;
    }
}