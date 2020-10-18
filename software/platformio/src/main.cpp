#include <Arduino.h>
#include <Wire.h>
#include <AS1115.h>
#include <BleKeyboard.h>

BleKeyboard bleKeyboard("Imperializer","Lustig Labs");

#define AS1115_ISR_PIN  33 ///< Interrupt pin connected to AS1115
#define SWITCH 15
#define BTN 27

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
#define negative 0xA

#define dim 1
#define bright 5 

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

unsigned long clear_timer;
unsigned int btn_hold_timer = 0;

int LED_1 = 11;
int LED_2 = 13;
int LED_3 = 10;
int LED_4 = 12;
int toggle = 9;

int options[4]  = {LED_1, LED_2, LED_3, LED_4};
int current_option = 0;

void keyPressed() {
  interrupted = true;
}

void displayConversion();
void blinkDigit();
double getMM(float input);
double getIN(float input);
double getMILE(float input);
double getKM(float input);
double getLB(float input);
double getKG(float input);
float getF(float input);
float getC(float input);


void setup() {
  pinMode(BTN, INPUT_PULLUP);
   for (int i=0; i<4; i++){
    pinMode(options[i],OUTPUT);
  }
  digitalWrite(options[0],HIGH); Serial.begin(115200);
  bleKeyboard.begin();

  Serial.print("Startup...");
  pinMode(AS1115_ISR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(AS1115_ISR_PIN), keyPressed, FALLING);

  pinMode(SWITCH,INPUT_PULLUP);

  Wire.begin();
  Wire.setClock(340000);
  as.selfAddress();
	as.init(8, bright);
  as2.init(8, bright);
  as.resume(true);
  as2.resume(true);
  
  as.read(); // reset any pending interrupt on the chip side
  as2.read(); // reset any pending interrupt on the chip side

  displayConversion();

  Serial.println("done");

  while((!digitalRead(BTN))){;;}

}

void loop() {
  if (interrupted){
    interrupted = false;
    uint16_t keyReg = ~as.read();

    if (keyReg){
      if (dotAdded){
        decimalPlace++;
      }
      else{
        counter *= 10;
      }
      switch (keyReg){
        case zero:
          bleKeyboard.print(0);
          break;
        case one:
          counter += 1*fractions[decimalPlace];
          bleKeyboard.print(1);
          break;
        case two:
          counter += 2*fractions[decimalPlace];
          bleKeyboard.print(2);
          break;
        case three:
          counter += 3*fractions[decimalPlace];
          bleKeyboard.print(3);
          break;
        case four:
          counter += 4*fractions[decimalPlace];
          bleKeyboard.print(4);
          break;
        case five:
          counter += 5*fractions[decimalPlace];
          bleKeyboard.print(5);
          break;
        case six:
          counter += 6*fractions[decimalPlace];
          bleKeyboard.print(6);
          break;
        case seven:
          counter += 7*fractions[decimalPlace];
          bleKeyboard.print(7);
          break;
        case eight:
          counter += 8*fractions[decimalPlace];
          bleKeyboard.print(8);
          break;
        case nine:
          counter += 9*fractions[decimalPlace];
          bleKeyboard.print(9);
          break;
        case dot:
          bleKeyboard.print('.');
          if (millis() - clear_timer < 400){
            counter = 0;
            dotAdded = false;
            decimalPlace = 0;
          }
          else if (!dotAdded){
            dotAdded = true;
            counter/=10;
          }
          clear_timer = millis();
          break;
        default: //if multiple keys are being pressed, undo our digit increment
          if (dotAdded){
            decimalPlace--;
          }
          else{
            counter /= 10;
          }
          break;
      }
      Serial.print(~keyReg & 0xFFFF,BIN);Serial.print(",");Serial.println(keyReg & 0xFFFF,HEX);
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
  if (!digitalRead(BTN)) {
    int count = 0;
    while (!digitalRead(BTN)){
      count++;
      if (count>15){
        as.shutdown(true);
        as2.shutdown(true);
        pinMode(BTN,OUTPUT);
        digitalWrite(BTN,LOW);
        delay(1000);
      }
      delay(50);
      if (blinkTimer++ > 2){
        blinkDigit();
        blinkTimer = 0;
      }
    }
    digitalWrite(options[current_option],LOW);
    current_option++; 
    if (current_option>3){
      current_option = 0;
    }
    digitalWrite(options[current_option],HIGH);
    delay(50);
    blinkTimer++;
    displayConversion();
  }
  else{
    btn_hold_timer = 0;
  }
}

void putNumber(double result, AS1115 *segDisp,byte places, bool isNegative = false){
  unsigned long whole_num = (unsigned long)result;
  unsigned long decimal_num = (result - whole_num)*multipliers[places+1];

  if (decimal_num%10 >= 5){ //round up
    decimal_num += 10;
    if (decimal_num>multipliers[places+1]-1){
      decimal_num = 0;
      whole_num++;
    }
  }
  decimal_num = decimal_num/10;
  byte decimals_used = places;
  for (int i=0; i<places; i++){
    if (decimal_num%10 == 0){ //ends with zero
      decimal_num = decimal_num/10;
      decimals_used--;
    }
  }

  uint8_t decimal = 0;
  if(dotAdded || decimal_num>0){
    decimal = 128;
  }

  //Display digits
  // show decimals
  for (int i = 0; i < decimals_used ; i++){
    segDisp->display(8-i, decimal_num % 10);
    decimal_num = decimal_num/10;
  }
  //show whole number
  bool checkedForNegative = false;
  for (int i = decimals_used; i<8; i++){
    if (whole_num){
      segDisp->display(8-i, whole_num % 10 + decimal);
      whole_num = whole_num/10;
    }
    else{
      if (i==decimals_used){
        segDisp->display(8-i, decimal);
      }
      else{
        segDisp->display(8-i, BLANK + decimal);
      }
      if (!checkedForNegative){
        if (isNegative){
          segDisp->display(8-i,negative);
        }
        checkedForNegative = true;
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
  switch (current_option){
    case 0:
      if(!currentMode){
        putNumber(getMM(counter),&as,4);
        putNumber(counter*1.0, &as2,4);
      }
      else{
        putNumber(counter*1.0,&as,4);
        putNumber(getIN(counter),&as2,4);
      }
      break;
    case 1:
      if(!currentMode){
        putNumber(getKM(counter),&as,2);
        putNumber(counter*1.0, &as2,2);
      }
      else{
        putNumber(counter*1.0,&as,2);
        putNumber(getMILE(counter),&as2,2);
      }
      break;
    case 2:
      if(!currentMode){
        putNumber(getKG(counter),&as,2);
        putNumber(counter*1.0, &as2,2);
      }
      else{
        putNumber(counter*1.0,&as,2);
        putNumber(getLB(counter),&as2,2);
      }
      break;
    case 3:
      if(!currentMode){
        putNumber(counter*1.0, &as2,1);
        float temp = getC(counter);
        if (temp<0){
          temp *= -1;
          putNumber(temp,&as,1,true);
        }
        else{
          putNumber(temp,&as,1);
        }
      }
      else{
        putNumber(counter*1.0,&as,1);
        putNumber(getF(counter),&as2,1);
      }
      break;
  }
}

double getMM(float input){
  return input*25.4;
}

double getIN(float input){
  return input/25.4;
}

float getF(float input){
  return input*9/5.0 + 32;
}

float getC(float input){
  return (input-32)*5/9.0;
}

double getLB(float input){
  return input*2.20462;
}

double getKG(float input){
  return input/2.20462;
}

double getMILE(float input){
  return input/1.60934;
}

double getKM(float input){
  return input*1.60934;
}

double getFT(float input){
  return input/1.60934;
}

double getM(float input){
  return input*1.60934;
}