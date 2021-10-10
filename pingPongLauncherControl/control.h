/***** Include Statements *****/
#include <Servo.h>
#include <Stepper.h>

/***** Constant definitions *****/
Servo loadServo;
Servo tiltServo;

int LOAD_SERVO_PIN = 4;
int LOAD_SPEED = 0; //(0,180) maps to (-1,1)* maxSpeed
int LOAD_TIME = 250; // Milliseconds of continuous servo movement to load one ball

int TILT_SERVO_PIN = 5;

int MOTOR_PIN = 6;

float PAN_SPEED = 15;

const int stepsPerRevolution = 2048;
Stepper panStepper = Stepper(stepsPerRevolution, 8, 10, 9, 11); //Numbers are pins for IN1, IN3, IN2, IN4
float currentAngle = 0; //Assume angle is 0 degrees at startup
int counts = 0; //will be used to calculate number of steps to move to new angle

//Initialise communication variables
String message;

float panAngle;
float tiltAngle;
int motorToggle;

/***** Function Definitions *****/
void load()
{
  ///Loads a ping pong ball using the continuous servo
  loadServo.attach(LOAD_SERVO_PIN);
  loadServo.write(LOAD_SPEED);
  delay(LOAD_TIME); //Could do this with millis() but don't need amazing precision and this is easier
  loadServo.write(89); //Stop loadServo
  Serial.println("l"); //sent to signify ball load is complete
  loadServo.detach();
}

void tilt(float angle)
{
  tiltServo.write(angle);
  Serial.println("t"); //sent to signify tilt move is complete
  //Serial.print(angle);
  //Serial.println(" degrees.");
}

void pan(float angle)
{
  Serial.print("Moving to ");
  Serial.print(angle);
  Serial.println(" degrees.");
  counts = stepsPerRevolution * (angle - currentAngle)/360;
  panStepper.step(counts);
  currentAngle = angle;
  Serial.println("p"); //sent to signify pan move is complete
  //Serial.println(currentAngle);
}

void switchMotor(int onOff)
{
  ///onOff=1 to turn motor on. onOff=0 to turn motor off
  digitalWrite(MOTOR_PIN,onOff);
  //Serial.print("Motor switched to ");
  Serial.println("m");//signifies motor toggle complete
}
