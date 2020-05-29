// Include this file after an IRController is included
#ifndef IRCONTROLLER_H
#define IRCONTROLLER_H

class IrController
{
public:
    int process_input(uint64_t);

private:
    int x;
};

#endif