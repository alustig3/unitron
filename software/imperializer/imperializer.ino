#include <Wire.h>
#include <AS1115.h>

#define AS1115_ISR_PIN  4 ///< Interrupt pin connected to AS1115
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

AS1115 as = AS1115(3);
AS1115 as2 = AS1115(1);

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

double fractions[5] = {1,.1,.01,.001,.0001};
unsigned long multipliers[9] = {1,10,100,1000,10000,100000,1000000,1000000,10000000};
byte places = 4;


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

  as2.init(8, bright);
	as2.clear();
  as2.read(); // reset any pending interrupt on the chip side

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
        decimalPlace++;
        Serial.println(decimalPlace);
      }
      else{
        counter *= 10;
      }
      switch (keyReg){
        case one:
          counter += 1*fractions[decimalPlace];break;
        case two:
          counter += 2*fractions[decimalPlace];break;
        case three:
          counter += 3*fractions[decimalPlace];break;
        case four:
          counter += 4*fractions[decimalPlace];break;
        case five:
          counter += 5*fractions[decimalPlace];break;
        case six:
          counter += 6*fractions[decimalPlace];break;
        case seven:
          counter += 7*fractions[decimalPlace];break;
        case eight:
          counter += 8*fractions[decimalPlace];break;
        case nine:
          counter += 9*fractions[decimalPlace];break;
        case dot:
          if (dotAdded){
            counter = 0;
            dotAdded = false;
            decimalPlace = 0;
          }
          else{
            dotAdded = true;
            counter/=10;
          }
          break;
      }
      Serial.println(counter,5);
      displayConversion();
    }
  }

  currentMode = !digitalRead(SWITCH);
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

void putNumber(double result, AS1115 *segDisp){
  unsigned long whole_num = (unsigned long)result;
  unsigned long decimal_num = (result - whole_num)*multipliers[places+1];

  Serial.print("whole,");
  Serial.println(whole_num);
  Serial.print("decimal,");
  Serial.println(decimal_num);
  if (decimal_num%10 >= 5){ //round up
    Serial.println("roundup");
    decimal_num += 10;
    if (decimal_num>multipliers[places+1]-1){
      decimal_num = 0;
      whole_num++;
    }
  }
  decimal_num = decimal_num/10;
  byte decimalDigit = places;
  for (int i=0; i<places; i++){
    if (decimal_num%10 == 0){ //ends with zero
      decimal_num = decimal_num/10;
      decimalDigit--;
    }
  }

  Serial.print("whole,");
  Serial.println(whole_num);
  Serial.print("decimal,");
  Serial.println(decimal_num);
  Serial.println();

  uint8_t decimal = 0;
  if(dotAdded || decimal_num>0){
    decimal = 128;
  }
  // show decimals
  byte decimal_length = 0;
  for (int i = 0; i < 8; i++){
    if (decimal_num){
      segDisp->display(8-i, decimal_num % 10);
      decimal_num = decimal_num/10;
      decimal_length++;
    }
  }
  
  for (int i = decimal_length; i<8; i++){
    if (whole_num){
      segDisp->display(8-i, whole_num % 10 + decimal);
      whole_num = whole_num/10;
    }
    else{
      if (i==decimal_length){
        segDisp->display(8-i, decimal);
      }
      else{
        segDisp->display(8-i, BLANK + decimal);
      }
    }
    decimal = 0;
  }
}

void blinkDigit(){
  if (currentMode){
    if (altBlink){
      as.setIntensity(dim);// blink all eight
    }
    else{
      as.setIntensity(bright);
      as2.setIntensity(bright);
    }
  }
  else{
    if (altBlink){
      as2.setIntensity(dim);// blink all eight
    }
    else{
      as2.setIntensity(bright);
      as.setIntensity(bright);
    }
  }

  altBlink = !altBlink;
}

void displayConversion(){
  if(currentMode){
    putNumber(counter*1.0, &as);
    putNumber(getMM(counter),&as2);
    // putNumber(getC(counter),currentMode);
  }
  else{
    putNumber(counter*1.0,&as2);
    putNumber(getIN(counter),&as);
    // putNumber(getF(counter),currentMode);
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