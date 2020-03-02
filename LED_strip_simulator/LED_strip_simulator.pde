void settings(){
  size(1300, 100);
}

int nLedsPerStripe = 120;
int ledSize = 6;
int ledDistance = 10;

int xOffset = 10;
int yOffset = 50;

LedStripe ledStripe_a = new LedStripe(10, 30, nLedsPerStripe, ledSize, ledDistance);
LedStripe ledStripe_b = new LedStripe(10, 50, nLedsPerStripe, ledSize, ledDistance);
LedStripe ledStripe_c = new LedStripe(10, 70, nLedsPerStripe, ledSize, ledDistance);

void logic_loop(){
 

}

void set_colors(){

  ledStripe_a.leds[1].setColor(50, 0, 0); 

}


void draw(){     
  ledStripe_a.draw();
  ledStripe_b.draw();
  ledStripe_c.draw();
}


class LedStripe {
  
  int x, y, nLeds, ledSize, ledDistance;
  
  Led[] leds;
  
  LedStripe(int x, int y, int nLeds, int ledSize, int ledDistance){
    this.x = x;
    this.y = y;
    this.nLeds = nLeds;
    this.ledSize = ledSize;
    this.ledDistance = ledDistance;
    this.leds = new Led[nLeds];
    
    for (int i=0; i<leds.length; i++){
      this.leds[i] = new Led(this.x + i*this.ledDistance, this.y, this.ledSize);
    }
    
  }
  
  void draw(){
    for (int i=0; i<leds.length; i++){
      this.leds[i].draw();
    }
  }
  
  void setLedColor(int i, int red, int green, int blue){
    this.leds[i].setColor(red, green, blue);
  }
}

class Led { 
  
  int x;
  int y;
  int size;
  int red, green, blue;

  // The Constructor is defined with arguments.
  Led(int x, int y, int size) { 
    this.x = x;
    this.y = y;
    this.size = size;
    
    this.red = 0;
    this.green = 0;
    this.blue = 0;
  }

  void draw() {
    stroke(0);
    fill(this.red, this.green, this.blue);
    circle(this.x, this.y, this.size);
  }
  
  void setColor(int red, int green, int blue){
    this.red = red;
    this.green = green;
    this.blue = blue;
  }
}
