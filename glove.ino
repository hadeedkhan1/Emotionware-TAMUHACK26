#include <LiquidCrystal.h>

// LCD pins: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

int motorPin = 9;
String incomingEmotion = "";

void setup() {
  Serial.begin(9600); // match Python
  pinMode(motorPin, OUTPUT);
  digitalWrite(motorPin, LOW);

  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("ON");
}

void loop() {
  // scout
  if (Serial.available() > 0) {
    incomingEmotion = Serial.readStringUntil('\n'); // read
    incomingEmotion.trim(); 

    if (incomingEmotion != "") {
      handleEmotion(incomingEmotion);
    }
  }
}

void handleEmotion(String emotion) {
  //Update
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Emotion Found:");
  lcd.setCursor(0, 1);
  lcd.print(emotion);

  if (emotion == "happy") {
    vibrate(100, 2);
  } 
  else if (emotion == "angry") {
    vibrate(500, 1);
  }
  else if (emotion == "sad") {
    vibrate(100, 1);
    vibrate(400, 1);
  }

  else if (emotion == "surprised") {
    vibrate(50, 3);
  }
  else if (emotion == "neutral") {
    vibrate(50, 1);
  }
}

void vibrate(int duration, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(motorPin, HIGH);
    delay(duration);
    digitalWrite(motorPin, LOW);
    delay(150);
  }
}
