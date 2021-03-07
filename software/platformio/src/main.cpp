#include <Arduino.h>
#include <Wire.h>
#include <AS1115.h>
#include <Adafruit_DotStar.h>
#include <SPI.h>         // COMMENT OUT THIS LINE FOR GEMMA OR TRINKET

#define AS1115_ISR_PIN  8 ///< Interrupt pin connected to AS1115
#define SWITCH 9
#define BTN 14

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
#define dot 0x8000
#define negative 0xA
#define NEG 0x2000
#define CLR 2048
#define UNIT 1024

#define dim 0
#define bright 5 

#define NUMPIXELS 12 // Number of LEDs in strip
Adafruit_DotStar strip(NUMPIXELS, DOTSTAR_BGR);

AS1115 btm_row = AS1115(3);
AS1115 top_row = AS1115(1);

volatile bool interrupted = false;
double counter = 0;
int offset = 0;
bool right = true;

bool lastMode = false;
bool currentMode = false;

int blinkTimer = 0;
bool altBlink = false;

uint8_t digits_shown = 1;

bool dotAdded = false;
bool input_negative = false;
int decimalPlace = 0;

double fractions[5] = {1,.1,.01,.001,.0001};
unsigned long multipliers[9] = {1,10,100,1000,10000,100000,1000000,1000000,10000000};

unsigned long clear_timer;
unsigned int btn_hold_timer = 0;


int current_option = 0;

unsigned long sleepTimer = 0;
unsigned int onDuration = 60000; // turn off after 5 minutes of inactivity
uint32_t yellow = 0xffff00;      // 'On' color (starts red)
uint32_t red = 0xff0000;      // 'On' color (starts red)


AS1115 *clearing_display;


void keyPressed() {
  interrupted = true;
}

void change_unit();
void displayConversion();
void blinkDigit();
double getMM(float input);
double getIN(float input);
double getFT(float input);
double getM(float input);
double getMILE(float input);
double getKM(float input);
double getLB(float input);
double getKG(float input);
double getOZ(float input);
double getML(float input);
float getF(float input);
float getC(float input);
void shutDown();
int readMem(unsigned int addr);
void writeMem(byte addr, byte data);


void setup() {
  pinMode(BTN, INPUT_PULLUP);

  pinMode(AS1115_ISR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(AS1115_ISR_PIN), keyPressed, FALLING);

  pinMode(SWITCH,INPUT_PULLUP);

  Wire.begin();
  Wire.setClock(340000);
  btm_row.selfAddress();
	btm_row.init(8, bright);
  top_row.init(8, bright);
  btm_row.resume(true);
  top_row.resume(true);
  
  btm_row.read(); // reset any pending interrupt on the chip side
  top_row.read(); // reset any pending interrupt on the chip side
  // writeMem(1,0);
  delay(20);
  current_option = readMem(1);

  displayConversion();

  strip.begin(); // Initialize pins for output
  strip.setBrightness(1);
  strip.show();  // Turn all LEDs off ASAP
  strip.show();  // Turn all LEDs off ASAP
  strip.show();  // Turn all LEDs off ASAP


  while((!digitalRead(BTN))){;;}
  sleepTimer =  millis();
}

void loop() {
  if ((millis()-sleepTimer)>onDuration){
    shutDown();
  }
  if (interrupted){
    uint16_t keyReg = ~btm_row.read();
    sleepTimer = millis();
    interrupted = false;

    if (keyReg){
      if (dotAdded){
        decimalPlace++;
      }
      else{
        counter *= 10;
      }
      switch (keyReg){
        case zero:
          break;
        case one:
          counter += 1*fractions[decimalPlace];
          break;
        case two:
          counter += 2*fractions[decimalPlace];
          break;
        case three:
          counter += 3*fractions[decimalPlace];
          break;
        case four:
          counter += 4*fractions[decimalPlace];
          break;
        case five:
          counter += 5*fractions[decimalPlace];
          break;
        case six:
          counter += 6*fractions[decimalPlace];
          break;
        case seven:
          counter += 7*fractions[decimalPlace];
          break;
        case eight:
          counter += 8*fractions[decimalPlace];
          break;
        case nine:
          counter += 9*fractions[decimalPlace];
          break;
        case CLR:
          counter = 0;
          dotAdded = false;
          decimalPlace = 0;
          input_negative = false;
          
          if (currentMode==0){
            clearing_display = &top_row;
          }
          else{
            clearing_display = &btm_row;
          }
          
          
          for (int i = clearing_display->digits_shown-1; i >= 0 ; i--){
            clearing_display->setIntensity(bright);
            clearing_display->display(8-i, 10);
          }
          delay(200);
          for (int i = clearing_display->digits_shown-1; i >= 0 ; i--){
            clearing_display->display(8-i, 15);
            // delay(20);
          }
          break;
        case NEG:
          input_negative  = !input_negative;
          if (dotAdded){
            decimalPlace--;
          }
          else{
            counter  = counter/10;
          }
          break;
        case UNIT:
          if (dotAdded){
            decimalPlace--;
          }
          else{
            counter/=10;
          }
          change_unit();
          break;
        case dot:
           if (!dotAdded){
            dotAdded = true;
            counter/=10;
          }
          else{
            decimalPlace--;
          }
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
      SerialUSB.print(~keyReg & 0xFFFF,BIN);SerialUSB.print(",");SerialUSB.println(keyReg & 0xFFFF,HEX);
      displayConversion();
    }
  }

  currentMode = !digitalRead(SWITCH);
  delay(50);
  if(lastMode!=currentMode){
    sleepTimer = millis();
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
    sleepTimer = millis();
    int count = 0;
    while (!digitalRead(BTN)){
      count++;
      if (count>6){
        shutDown();
        delay(1000);
      }
      delay(50);
      if (blinkTimer++ > 2){
        blinkDigit();
        blinkTimer = 0;
      }
    }

  }
  else{
    btn_hold_timer = 0;
  }
}


void change_unit(){
    strip.setPixelColor(10-2*current_option + 1, 0);
    strip.setPixelColor(10-2*current_option, 0);
    current_option++; 
    if (current_option>5){
      current_option = 0;
    }
    strip.setPixelColor(10-2*current_option + 1, yellow);
    strip.setPixelColor(10-2*current_option, red);
    strip.show();
    delay(50);
    blinkTimer++;
    displayConversion();
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
  digits_shown = decimals_used;
  bool checkedForNegative = false;
  for (int i = decimals_used; i<8; i++){
    if (whole_num){
      segDisp->display(8-i, whole_num % 10 + decimal);
      whole_num = whole_num/10;
      digits_shown++;
    }
    else{ // 0 or blank preceding digits or negative sign
      if (i==decimals_used){ // if we're at the 1's place then show 0 or 0.
        segDisp->display(8-i, decimal);
        digits_shown++;
      }
      else{ // otherwise we are preceding the 1's place, so give it a blank or a negative
        segDisp->display(8-i, BLANK);
        if (!checkedForNegative){
          if (isNegative){
            segDisp->display(8-i,negative);
          }
          checkedForNegative = true;
        }
      }
    }
    decimal = 0;
  }
  segDisp->digits_shown = digits_shown;
}

void blinkDigit(){
  int dotstar_pos = 10-2*current_option;
  if (currentMode){
    if (altBlink){
      strip.setPixelColor(dotstar_pos + 1, 0); 
      btm_row.setIntensity(dim);// blink all eight
    }
    else{
      strip.setPixelColor(dotstar_pos + 1, yellow);
      strip.setPixelColor(dotstar_pos, red);
      btm_row.setIntensity(bright);
      top_row.setIntensity(bright);
    }
  }
  else{
    if (altBlink){
      strip.setPixelColor(dotstar_pos, 0); 
      top_row.setIntensity(dim);// blink all eight
    }
    else{
      strip.setPixelColor(dotstar_pos + 1, yellow);
      strip.setPixelColor(dotstar_pos, red);
      btm_row.setIntensity(bright);
      top_row.setIntensity(bright);
    }
  }
  strip.show();
  altBlink = !altBlink;
}

void displayConversion(){
  switch (current_option){
    case 0:
      if(!currentMode){
        putNumber(getMM(counter),&btm_row,4,input_negative);
        putNumber(counter*1.0, &top_row,4,input_negative);
      }
      else{
        putNumber(counter*1.0,&btm_row,4,input_negative);
        putNumber(getIN(counter),&top_row,4,input_negative);
      }
      break;
    case 1:
      if(!currentMode){
        putNumber(getM(counter),&btm_row,2,input_negative);
        putNumber(counter*1.0, &top_row,2,input_negative);
      }
      else{
        putNumber(counter*1.0,&btm_row,2,input_negative);
        putNumber(getFT(counter),&top_row,2,input_negative);
      }
      break;
    case 2:
      if(!currentMode){
        putNumber(getKM(counter),&btm_row,2,input_negative);
        putNumber(counter*1.0, &top_row,2,input_negative);
      }
      else{
        putNumber(counter*1.0,&btm_row,2,input_negative);
        putNumber(getMILE(counter),&top_row,2,input_negative);
      }
      break;
    case 3:
      if(!currentMode){
        putNumber(getKG(counter),&btm_row,2,input_negative);
        putNumber(counter*1.0, &top_row,2,input_negative);
      }
      else{
        putNumber(counter*1.0,&btm_row,2,input_negative);
        putNumber(getLB(counter),&top_row,2,input_negative);
      }
      break;
    case 4:
      float temp;
      if(!currentMode){
        putNumber(counter*1.0, &top_row,1,input_negative);
        if(input_negative){
          temp = getC(-counter);
        }
        else{
          temp = getC(counter);
        }
        if (temp<0){
          temp *= -1;
          putNumber(temp,&btm_row,1,true);
        }
        else{
          putNumber(temp,&btm_row,1);
        }
      }
      else{
        putNumber(counter*1.0,&btm_row,1,input_negative);
        if(input_negative){
          temp = getF(-counter);
        }
        else{
          temp = getF(counter);
        }
        if (temp<0){
          temp *= -1;
          putNumber(temp,&top_row,1,true);
        }
        else{
          putNumber(temp,&top_row,1);
        }
      }
      break;
    case 5:
      if(!currentMode){
        putNumber(getML(counter),&btm_row,2,input_negative);
        putNumber(counter*1.0, &top_row,2,input_negative);
      }
      else{
        putNumber(counter*1.0,&btm_row,2,input_negative);
        putNumber(getOZ(counter),&top_row,2,input_negative);
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
  return input*3.28084;
}

double getM(float input){
  return input/3.28084;
}

double getOZ(float input){
  return input/29.5735;
}

double getML(float input){
  return input*29.5735;
}


void shutDown(){
  writeMem(1,current_option);
  btm_row.shutdown(true);
  top_row.shutdown(true);
  strip.setPixelColor(10-2*current_option, 0);
  strip.setPixelColor(10-2*current_option + 1, 0);
  strip.show();
  pinMode(BTN,OUTPUT);
  digitalWrite(BTN,LOW);
}

void writeMem(byte addr, byte data){
  Wire.beginTransmission(0x50);
  Wire.write(addr);
  Wire.write(data);
  Wire.endTransmission();
}

int readMem(unsigned int addr) {
  Wire.beginTransmission(0x50);
  Wire.write(addr);
  Wire.endTransmission();

  Wire.requestFrom(0x50,1);
  int data = -1;
  if (Wire.available()){
    data = Wire.read();
  }
  return data;
}