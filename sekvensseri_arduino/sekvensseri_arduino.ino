void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  DDRC = 0xFF;
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()) {
    PORTC = Serial.read();
  }
}

