#include "AS1115.h"

#define DIGITS	0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70, 0x7F, 0x7B, 0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47, 

//uppercase letters		A,    b,    C,    d     E     F     G     H     I     J     K     L     M
//                      n     o     P     q     r     s     t     U     v     W     X     y     Z
#define LETTERS			0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47, 0x5E, 0x37, 0x30, 0x3C, 0x2F, 0x0E, 0x54, \
                        0x15, 0x1D, 0x67, 0x73, 0x05, 0x5B, 0x0F, 0x3E, 0x1C, 0x2A, 0x49, 0x3B, 0x25

//TODO : to be save in flash memory ??
const uint8_t digits[16] = { DIGITS };
const uint8_t letters[26] = { LETTERS };


AS1115::AS1115(uint8_t addr) {
	_deviceAddr = addr;
}

AS1115::~AS1115() {}


void AS1115::selfAddress(){
	Wire.beginTransmission(0x00);
	Wire.write(SHUTDOWN);
	Wire.write(NORMAL_OPERATION | RESET_FEATURE);
	Wire.endTransmission();

	if(_deviceAddr != 0x00) {
		delay(10);
		Wire.beginTransmission(0x00);
		Wire.write(SELF_ADDRESSING);
		Wire.write(1);
		Wire.endTransmission();
	}
}

void AS1115::init(uint8_t digits, uint8_t intensity)
{
	_digits = digits;
	writeRegister(SHUTDOWN, NORMAL_OPERATION | RESET_FEATURE);
	writeRegister(DECODE_MODE, 0xFF);
	writeRegister(SCAN_LIMIT, digits - 1);
	setIntensity(intensity);
}

void AS1115::setIntensity(uint8_t intensity)
{
	writeRegister(GLOBAL_INTENSITY, intensity);
}

void AS1115::setBankIntensity(bool bank, uint8_t intensity){
	if (bank == 0){
		writeRegister(DIG01_INTENSITY, (intensity<<4|intensity));
		writeRegister(DIG23_INTENSITY, (intensity<<4|intensity));
	}
	else{
		writeRegister(DIG45_INTENSITY,(intensity<<4|intensity));
		writeRegister(DIG67_INTENSITY,(intensity<<4|intensity));
	}
}

void AS1115::shutdown(bool preserve)
{
	writeRegister(SHUTDOWN, SHUTDOWN_MODE | (preserve ? PRESERVE_FEATURE : RESET_FEATURE));
}

void AS1115::resume(bool preserve)
{
	writeRegister(SHUTDOWN, NORMAL_OPERATION | (preserve ? PRESERVE_FEATURE : RESET_FEATURE));
}

void AS1115::clear()
{
	int n = _digits;

	Wire.beginTransmission(_deviceAddr);
	Wire.write(DIGIT0);  //first digit to write is #1

	while (n--) {
		Wire.write(AS1115_BLANK);
	}

	Wire.endTransmission();
}

void AS1115::display(uint8_t digit, uint8_t value)
{
	writeRegister((AS1115_REGISTER)(DIGIT0 + digit - 1), value);
}

uint8_t AS1115::readPort(uint8_t port)
{
	uint8_t value = readRegister(KEY_A + port);
	//self-adrressing disable the two LSB of KEY_A 
	// if(port == 0 && _deviceAddr != 0x00) return value && 0xFC;

	return value;
}

uint16_t AS1115::read()
{
	uint8_t a = readPort(0);
	uint8_t b = readPort(1);

	return a<<8 | b;
}

void AS1115::writeRegister(AS1115_REGISTER reg, uint8_t value)
{
	Wire.beginTransmission(_deviceAddr);
	Wire.write(reg);
	Wire.write(value);
	Wire.endTransmission();
	delay(1);
}

uint8_t AS1115::readRegister(AS1115_REGISTER reg)
{
	Wire.beginTransmission(_deviceAddr);
	Wire.write(reg);
	Wire.endTransmission();
	Wire.requestFrom(_deviceAddr, (uint8_t)1);
	return Wire.read();
}