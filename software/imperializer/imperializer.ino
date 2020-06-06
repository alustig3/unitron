#include <Wire.h>
#include <AS1115.h>


#define AS1115_ISR_PIN  2 ///< Interrupt pin connected to AS1115
#define SWITCH 3
#define BLANK 15

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

  pinMode(SWITCH,INPUT_PULLUP);

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

  currentMode = digitalRead(SWITCH);
  delay(50);
  if(lastMode!=currentMode){
    if(digitalRead(SWITCH)){
      putNumber(-1);
      right = false;
      putNumber(counter);
    }
    else{
      putNumber(-1);
      right = true;
      putNumber(counter);
    }
  }
  lastMode = currentMode;

}

void putNumber(int number){

  if (number>999){
    as.display(1 + 4*right, number%10000/1000);
  }
  else{
    as.display(1 + 4*right, BLANK);
  }

  if (number>99){
    as.display(2 + 4*right, number%1000/100);
  }
  else{
    as.display(2 + 4*right, BLANK);
  }

  if (number>9){
    as.display(3 + 4*right, number%100/10+128);
  }
  else{
    as.display(3 + 4*right, BLANK);
  }

  if (number>0){
    as.display(4 + 4*right, number%10);
  }
  else{
    as.display(4 + 4*right, BLANK);
  }
}