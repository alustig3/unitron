#include <Wire.h>
#include <AS1115.h>


#define AS1115_ISR_PIN  2 ///< Interrupt pin connected to AS1115
#define switch 3

AS1115 as = AS1115(0x00);

volatile bool interrupted = false;
int counter = 0;
int offset = 0;
bool right = true;

bool lastMode = false;
bool currentMode = false;


void keyPressed() {
    interrupted = true;
}

void setup() {
  Serial.begin(115200);

  pinMode(AS1115_ISR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(AS1115_ISR_PIN), keyPressed, FALLING);

  pinMode(switch,INPUT_PULLUP);

  Wire.begin();
	as.init(8, 13);
	as.clear();
  as.read(); // reset any pending interrupt on the chip side
}

void loop() {
  // put your main code here, to run repeatedly:
  if (interrupted){
    interrupted = false;
    uint8_t regA = ~as.readPort(0);
    uint8_t regB = ~as.readPort(1);
    uint16_t keyReg = regA<<8 | regB;
    Serial.println(keyReg,HEX);
    if (keyReg){
      counter++;
      putNumber(counter);
    }
  }

  currentMode = digitalRead(switch);
  delay(50);
  if(lastMode!=currentMode){
    if(digitalRead(switch)){
      putNumber(0);
      right = false;
      putNumber(counter);
    }
    else{
      putNumber(0);
      right = true;
      putNumber(counter);
    }
  }
  lastMode = currentMode;

}

void putNumber(int number){
  as.display(1 + 4*right, number%10000/1000);
  as.display(2 + 4*right, number%1000/100);
  as.display(3 + 4*right, number%100/10+128);
  as.display(4 + 4*right, number%10);
}