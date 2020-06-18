int mqAPin=A0;
int mqDPin=2;
int mqBite=0;
int  mqVal=0;
float mqVot=0;

void setup(){
Serial.begin(9600);
pinMode(mqAPin, INPUT);
}

void loop(){
mqVal = analogRead(mqAPin);

//  将ADC输出值转换为模拟电压值
mqVot = mqVal*0.0049;   
Serial.println(mqVot);

mqBite = digitalRead(mqDPin);
if (mqBite == 1){
  Serial.println("一氧化碳浓度正常！");
  }
else{
    Serial.println("一氧化碳浓度超标！！！");
    }
    
delay(1000);
}
