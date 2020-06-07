#include <Wire.h>
#include <AS1115.h>


#define AS1115_ISR_PIN  2 ///< Interrupt pin connected to AS1115
#define SWITCH 3
#define BLANK 15

#define zero 0x1000
#define one 0x40
#define two 0x20
#define three 0x10
#define four 0x4
#define five 0x2
#define six 0x1
#define seven 0x8
#define eight 0x80
#define nine 0x4000
#define dot 0x2000

AS1115 as = AS1115(0x00);

volatile bool interrupted = false;
int counter = 0;
int offset = 0;
bool right = true;

bool lastMode = false;
bool currentMode = false;

uint8_t digit = 0;


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
      counter *= 10;
      switch (keyReg){
        case zero:
          counter += 0;break;
        case one:
          counter += 1;break;
        case two:
          counter += 2;break;
        case three:
          counter += 3;break;
        case four:
          counter += 4;break;
        case five:
          counter += 5;break;
        case six:
          counter += 6;break;
        case seven:
          counter += 7;break;
        case eight:
          counter += 8;break;
        case nine:
          counter += 9;break;
        case dot:
          counter = 0;break;
      }
      if(digitalRead(SWITCH)){
        putNumber(counter,0);
        putNumber(counter*2,1);
      }
      else{
        putNumber(counter/2,0);
        putNumber(counter,1);
      }
    }
  }

  currentMode = digitalRead(SWITCH);
  delay(50);
  if(lastMode!=currentMode){
    if(digitalRead(SWITCH)){
      putNumber(counter,0);
      putNumber(counter*2,1);
    }
    else{
      putNumber(counter/2,0);
      putNumber(counter,1);
    }
  }
  lastMode = currentMode;
}

void putNumber(int number, bool right){

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
    as.display(3 + 4*right, number%100/10);
  }
  else{
    as.display(3 + 4*right, BLANK);
  }

  if (number>-1){
    as.display(4 + 4*right, number%10);
  }
  else{
    as.display(4 + 4*right, BLANK);
  }
}