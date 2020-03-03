#include <FastLED.h>

#define LED_PIN       5
#define NUM_LEDS      62
#define BRIGHTNESS    64
#define LED_TYPE      WS2811
#define COLOR_ORDER   GRB
CRGB leds[NUM_LEDS];

void clear(){
  for(int dot = 0; dot < NUM_LEDS; dot++){
//    leds[dot] = CRGB::Black;
    leds[dot] = CRGB(10, 0, 0);
  }
}



class Chaser {

  private:
    int position;
    int length;
    int red;
    int green;
    int blue;
    int direction;
    int speed;
    
  public:

    Chaser(
        int position, 
        int length, 
        int red, 
        int green, 
        int blue, 
        int speed,
        int direction
     ){
      
      this->position = position;
      this->length = length;
      this->red = red;
      this->green = green;
      this->blue = blue;
      this->direction = direction;
      this->speed = speed;

      void set_color(int red, int green, int blue);
      void say_hi();
    }

    void set_color(int red, int green, int blue){
        this->red = red;
        this->green = green;
        this->blue = blue;
    }

    void say_hi(){
      Serial.println("Hi");  
    }

    void setup(){
    }
    
    void loop(){

      leds[this->position] = CRGB(this->red, this->green, this->blue);//CRGB::Red;
//      
//      char b[30];
//      sprintf(b, "led %d,%d,%d", leds[this->position].r, leds[this->position].g, leds[this->position].b);
//      Serial.println(b);
//      
//      char buffer[30];
//      sprintf(buffer, "position: %d, length: %d", this->position, this->length);
//      Serial.println(buffer);
//      
      this->position = this->position + this->speed * this->direction;
      
      if(this->position > this->length){
        this->position = 0;
      }

      if(this->position < 0){
        this->position = this->length;
      }      
    }
};

//Chaser* chasers; 
//Chaser chaser1(0, NUM_LEDS, 200, 0, 100, 1, -1);
//Chaser chaser2(5, NUM_LEDS, 100, 10, 200, 4, 1);

Chaser *chasers[15];

void setup() {
//  Serial.begin(9600);
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
  
//  for(int i = 0; i < 10; i++){
//    chasers[i] = new Chaser(i, NUM_LEDS, 200, 0, 100, 1, -1);
//  }
//  chasers[0] = new Chaser(0, NUM_LEDS, 200, 0, 100, 1, -1);
  
//   red slow
  for(int i = 0; i<3; i++){
    chasers[i] = new Chaser(i, NUM_LEDS, (i+1)*20, 0, 0, 4, -1);
  }
////
//  // red fast
//  for(int i = 3; i<6; i++){
//    chasers[i] = new Chaser(i, NUM_LEDS, i*50, 10, 0, 2, -1);
//  }
////
  //green slow
  for(int i = 6; i<15; i++){
    chasers[i] = new Chaser(i, NUM_LEDS, i*10, 100, 20, 1, 1);
  }

//  chasers[0] = new Chaser(0, NUM_LEDS, 200, 0, 0, 0, 1);
//  chasers[1] = new Chaser(1, NUM_LEDS, 200, 0, 0, 0, 1);
//  chasers[2] = new Chaser(2, NUM_LEDS, 200, 0, 0, 0, 1);
//  chasers[3] = new Chaser(3, NUM_LEDS, 200, 0, 0, 0, 1);
//  chasers[4] = new Chaser(4, NUM_LEDS, 200, 0, 0, 0, 1);
//  chasers[5] = new Chaser(5, NUM_LEDS, 10, 0, 0, 0, 1);
//  chasers[6] = new Chaser(6, NUM_LEDS, 10, 0, 0, 0, 1);
//  chasers[7] = new Chaser(7, NUM_LEDS, 10, 0, 0, 0, 1);
//  chasers[8] = new Chaser(8, NUM_LEDS, 10, 0, 0, 0, 1);
//  chasers[9] = new Chaser(9, NUM_LEDS, 10, 0, 0, 0, 1);
  
}



void loop() {
  clear();
//  chaser1.loop();
//  chaser2.loop();

  for(int i = 0; i<10; i++){
    chasers[i]->loop();
  }
  FastLED.show();
  delay(50);
  
}
