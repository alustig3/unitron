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

#define dim 2
#define bright 15

AS1115 as = AS1115(0x00);

volatile bool interrupted = false;
double counter = 0;
int offset = 0;
bool right = true;

bool lastMode = false;
bool currentMode = false;

int blinkTimer = 0;
bool altBlink = false;

uint8_t digit = 0;

bool dotAdded = false;
int decimalPlace = 0;

void keyPressed() {
  interrupted = true;
}

void setup() {
  Serial.begin(115200);
  Serial.print("Startup...");

  pinMode(AS1115_ISR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(AS1115_ISR_PIN), keyPressed, FALLING);

  pinMode(SWITCH,INPUT_PULLUP);

  Wire.begin();
	as.init(8, bright);
	as.clear();
  as.read(); // reset any pending interrupt on the chip side

  displayConversion();
  Serial.println("done");
}

void loop() {
  // put your main code here, to run repeatedly:
  if (interrupted){
    interrupted = false;
    uint8_t regA = ~as.readPort(0);
    uint8_t regB = ~as.readPort(1);
    uint16_t keyReg = regA<<8 | regB;

    if (keyReg){
      if (dotAdded){
        decimalPlace--;
        Serial.println(decimalPlace);
      }
      else{
        counter *= 10;
      }
      switch (keyReg){
        case one:
          counter += 1*pow(10,decimalPlace);break;
        case two:
          counter += 2*pow(10,decimalPlace);break;
        case three:
          counter += 3*pow(10,decimalPlace);break;
        case four:
          counter += 4*pow(10,decimalPlace);break;
        case five:
          counter += 5*pow(10,decimalPlace);break;
        case six:
          counter += 6*pow(10,decimalPlace);break;
        case seven:
          counter += 7*pow(10,decimalPlace);break;
        case eight:
          counter += 8*pow(10,decimalPlace);break;
        case nine:
          counter += 9*pow(10,decimalPlace);break;
        case dot:
          if (dotAdded){
            counter = 0;
            dotAdded = false;
            decimalPlace = 0;
          }
          else if (counter){
            dotAdded = true;
            counter/=10;
          }
          break;
      }
      Serial.println(counter);
      displayConversion();
    }
  }

  currentMode = digitalRead(SWITCH);
  delay(50);
  if(lastMode!=currentMode){
    displayConversion();
    altBlink = !altBlink;
    blinkDigit();
  }
  lastMode = currentMode;

  if (blinkTimer++ > 2){
    blinkDigit();
    blinkTimer = 0;
  }
}

void putNumber(double result, bool right){
  byte places = 2;
  unsigned long number;
  unsigned long dispNum = (unsigned long)(result*pow(10,1+places));
  if (dispNum%10 >= 5){ //round up
    dispNum += 10;
  }
  dispNum = (dispNum - dispNum%10)/10;
  number = dispNum;
  byte decimalDigit = places;
  for (int i=0; i<places; i++){
    if (number%10 == 0){ //whole number
      number = number/10;
      decimalDigit--;
    }
  }
  int multipliers[4] = {10,100,1000,10000};
  for (byte i=3; i>0 ; i--){
    Serial.println(i);
    uint8_t decimal = 0;
    if (i == decimalDigit){
      decimal = 128;
    }
    if (number>=pow(10,i)){
      as.display((4-i) + 4*right, number%multipliers[i]/multipliers[i-1] + decimal);
    }
    else{
      as.display((4-i) + 4*right, BLANK + decimal);
    }
  }
  if (number >= 0){
    if ((dotAdded==true) && (decimalPlace==0) && (currentMode!=right)){
      as.display(4 + 4*right, number%10 + 128);
    }
    else{
      as.display(4 + 4*right, number%10);
    }
  }
  else{
    as.display(4 + 4*right, BLANK);
  }
}

void blinkDigit(){
  if (altBlink){
    as.setBankIntensity(!currentMode,dim);
    as.setBankIntensity(currentMode,bright);
    // as.setIntensity(dim);// blink all eight
  }
  else{
    as.setBankIntensity(!currentMode,bright);
    // as.setIntensity(bright);
  }
  altBlink = !altBlink;
}

void displayConversion(){
  if(currentMode){
    putNumber(counter*1.0,!currentMode);
    putNumber(getMM(counter),currentMode);
    // putNumber(getC(counter),currentMode);
  }
  else{
    putNumber(getIN(counter),currentMode);
    // putNumber(getF(counter),currentMode);
    putNumber(counter*1.0,!currentMode);
  }
}

double getMM(float input){
  return input*25.4;
}

double getIN(float input){
  return input/25.4;
}

double getF(float input){
  return input*9/5.0 + 32;
}

double getC(float input){
  return (input-32)*5/9.0;
}