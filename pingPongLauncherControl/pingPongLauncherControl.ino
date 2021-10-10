#include "control.h"

void setup()
{
  // Start serial
  Serial.begin(9600);
  Serial.setTimeout(250); //Default timeout is 1000ms which slows down communication too much. 
        //We lower the timout as a backup but also read until we find a terminating character '/r'
  Serial.println("Ping Pong Launcher control is active");
  
  // Set up continuous servo
  // Loading servo is not attached here as it is attached and detached for each load cycle
  
  // Set up tilt servo
  tiltServo.attach(TILT_SERVO_PIN);
  // Set up motor transistor
  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW);

  // Set up stepper motor
  panStepper.setSpeed(PAN_SPEED);

}

void loop()
{
  //Listen for incoming instructions over serial
  if(Serial.available()){
    message = Serial.readStringUntil('\r');

    // say what you got:
    //Serial.print("I received: ");
    //Serial.println(message);

    //Interpret message
    if(message.indexOf("load") >= 0){
      load();
    }
    else if (message.indexOf("pan") >= 0){
      //Serial.println("Pan command received");
      panAngle = message.substring(3).toFloat();
      //Serial.print("Panning to ");
      //Serial.print(panAngle);
      //Serial.println(" degrees");
      pan(panAngle);
    }
    else if (message.indexOf("tilt") >= 0){
      //Serial.println("Tilt command received");
      tiltAngle = message.substring(4).toFloat();
      //Serial.print("Tilting to ");
      //Serial.print(tiltAngle);
      //Serial.println(" degrees");
      tilt(tiltAngle);
    }
    else if (message.indexOf("motor") >= 0){
      //Serial.println("Pan command received");
      motorToggle = message.substring(5).toInt();
      //Serial.print("Launch motors set to ");
      //Serial.println(motorToggle);
      switchMotor(motorToggle);
    }
  }
}
