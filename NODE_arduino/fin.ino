//include lib
#include <ArduinoJson.h>
#include <Stepper.h>
#include <LiquidCrystal.h>
#include <SoftwareSerial.h>
#include <WiFi.h>

//json
const String Node="Node_01";
const String Control="Sensor_Data";
const String Function="N2F";
String Type_of_MSG="Normal";
int Heart_Beat=0;
int Bump=0;
const String Source="GW_01";
//init
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
Stepper myStepper(200,15,16,17,18);
SoftwareSerial ESP8266(10, 9);
StaticJsonBuffer<200> upbuffer;
StaticJsonBuffer<200> rebuffer;
JsonObject& up = upbuffer.createObject();

//def
const String SSID="TWISC";//Wifi名稱
const String PASSWORD="706@TWISC";//Wifi密碼
const int sensorPin = A0;
const double alpha = 0.75;              // smoothing參數 可自行調整0~1之間的值
const double beta = 0.5;                // find peak參數 可自行調整0~1之間的值
const int period = 20;                  // sample脈搏的delay period
const int trig = 7;
const int echo = 6;
const int inter_time = 1000;
int time = 0;
bool wifiReady = false;
bool f2m = false;
String lcdwd="";

void setup() {
  // put your setup code here, to run once:
  lcd.begin(16, 2);                   //lcd
  myStepper.setSpeed(60);             //motor
  
  Serial.begin(9600);
  ESP8266.begin(9600);
  
  pinMode (trig, OUTPUT);
  pinMode (echo, INPUT);

 up["Node"]=Node;
  up["Control"]=Control;
  up["Function"]=Function;
  up["Type_of_MSG"]=Type_of_MSG;
  JsonArray& Data = up.createNestedArray("Data");
  Data.add(Heart_Beat);
  Data.add(Bump);
  up["Source"]=Source;  

}

void loop() {
  // put your main code here, to run repeatedly:
   //delay(1000);
   //wifi   
   if(wifiReady){
    proxyToESP8266();
    senseHeartRate();
    hcsr();
    jsonup();
    stepper();
    String line=readLine();
    if(f2m){
      
       jsonrd();
      }        
    }
   else{
    if(!connectToWifi())
      delay(2000);
    }
}
void stepper() {
  // step one revolution  in one direction:
  myStepper.step(200);
  //delay(500);
}
void hcsr() {
  float duration, distance;
  digitalWrite(trig, HIGH);
  delayMicroseconds(1000);
  digitalWrite(trig, LOW);
  duration = pulseIn (echo, HIGH);
  distance = (duration/2)/29;
  if(distance<5){
    Type_of_MSG="Emergency";
    Bump=1;    
    lcdwd="bump";
    lcd.setCursor(0, 0);
    lcd.print(lcdwd);
  }
  else{
    Bump=0;
    lcdwd="";
    Type_of_MSG="Normal";
    }
  lcd.setCursor(0, 0);
  lcd.print(lcdwd);
  delay(inter_time);
}
void senseHeartRate()
{
    int count = 0;                              // 記錄心跳次數
    double oldValue = 0;                        // 記錄上一次sense到的值
    double oldChange = 0;                       // 記錄上一次值的改變
       
    unsigned long startTime = millis();         // 記錄開始測量時間
   
    while(millis() - startTime < 5000) {       // sense 10 seconds
        int rawValue = analogRead(sensorPin);   // 讀取心跳sensor的值
        double value = alpha*oldValue + (1-alpha)*rawValue;     //smoothing value
   
        //find peak
        double change = value-oldValue;         // 計算跟上一次值的改變量
        if (change>beta && oldChange<-beta) {   // heart beat
            count = count + 1;
        }
         
        oldValue = value;
        oldChange = change;
        delay(period);
    }
    Heart_Beat=count*12;
    lcd.setCursor(0, 1);
    lcd.print(Heart_Beat);
    //BTSerial.println(count*6);          //use bluetooth to send result to android
}
void jsonup(){
  
  
  sendCmd("AT+CIPSEND=133");
  up.printTo(ESP8266);
  up.printTo(Serial);
  Serial.println();
  sendCmd("");  
}
void jsonrd(){
  
  
}
//等候特定的回應出現
//timeout 逾時時間，超過此時間，則會停止等待。
//keyword1,keyword2 在回應中要等候出現的關鍵字。
//如果關鍵字出現，就傳回 true，如果逾時都沒等到，就傳回 false。
bool waitForResponse(int timeout,String keyword1,String keyword2=""){
  bool found = false;
  while(true){
    String response = readLine();
    found = findKeyword(response,keyword1) || findKeyword(response,keyword2);
    if(found || timeout<=0){//找到或時間到則跳出
      // ESP8266.flush();
      break;
    }else{//再等一下
      delay(10);
      timeout-=10;
      if(response!=""){//雖然沒找到關鍵字，但至少有一行回應，給予加碼時間。
        timeout+=100;
      }
    }
  }
  return found;
}
//連線到 Wifi，並將 ESP8266設置為伺服器模式。
//成功則傳回 true，否則傳回 false。
bool connectToWifi(){
  wifiReady=false;
  log("Contacting ESP8266...");
  sendCmd("AT");
  // 成功連線到 ESP8266
  if(waitForResponse(1000,"OK\r\n")){
    log("Got response from ESP8266.");
    log("Connecting to wifi...");
    sendCmd("AT+CWJAP=\""+SSID+"\",\""+PASSWORD+"\""); //注意，這裡使用了斜線「\」作為跳脫字元，以便在引號當中使用引號符號。
    if(waitForResponse(6000,"OK\r\n")){
    log("Wifi connected.");
    sendCmd("AT+CIPSTART=\"TCP\",\"10.0.1.25\",8880");      
    if(waitForResponse(1000,"OK\r\n"))
    {
       log("link ok");
       wifiReady=true;   
    }
 //wifiReady=true;   
    }else{
      log("ERROR: Failed to connect to Wifi.");
    }
  }else{//沒有成功連線：無法取得 OK回應。
    log("ERROR: Failed to contact ESP8266.");
  }
  return wifiReady;
}
//傳送命令並等候 ESP8266的回應
//cmdString 命令
void sendCmd(String cmdString){
  cmdString=cmdString+"\r\n";
  ESP8266.print(cmdString);
  ESP8266.flush();
}
//加入記錄
void log(String msg){
    Serial.println(msg);
}
//指出字串中是否包含指定的關鍵字
//常用關鍵字："OK\r\n","ERROR\r\n","no change\r\n","no this fun\r\n"
bool findKeyword(String text,String keyword){
  if(keyword==""){
    return false;
  }
  return text.lastIndexOf(keyword)>-1;
}
//讀取一行文字
String readLine(){
  String lineString="";
  while(ESP8266.available()){
    char inChar = ESP8266.read();
    if(inChar=='+'){
      f2m=true;
    }
    lineString=lineString+String(inChar);
    if(inChar=='\n'){
      break;
    }
    
  }
  return lineString;
}
void proxyToESP8266(){
  while (Serial.available()) {
    int inByte = Serial.read();
    ESP8266.write(inByte);
  }
}
