#include <Wire.h>
#include <AS1115.h>


#define AS1115_ISR_PIN  2 ///< Interrupt pin connected to AS1115
#define switch 3

AS1115 as = AS1115(0x00);

volatile bool interrupted = false;
int counter = 0;
int offset = 0;
bool right = true;

void keyPressed() {
    interrupted = true;
}

void setup() {
  Serial.begin(115200);

  pinMode(AS1115_ISR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(AS1115_ISR_PIN), keyPressed, FALLING);

  pinMode(switch,INPUT_PULLUP);

  Wire.begin();
	as.init(8, 1);
	as.clear();
  as.read(); // reset any pending interrupt on the chip side


}

void loop() {
  // put your main code here, to run repeatedly:
  if (interrupted){
    counter++;
    interrupted = false;
    delay(150);
    uint8_t areg = ~as.readPort(0);
    uint8_t breg = ~as.readPort(1);
    Serial.print(areg,BIN);
    Serial.print("\t");
    Serial.println(breg,BIN);
    as.display(1 + 4*right, counter/1000);
    as.display(2 + 4*right, counter/100);
    as.display(3 + 4*right, counter/10+128);
    as.display(4 + 4*right, counter%10);
  }

  if(digitalRead(switch)){
    right = false;
  }
  else{
    right = true;
  }

}
