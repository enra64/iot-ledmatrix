#include <FastLED.h>

#define NUM_LEDS_CURRENT 100//160
#define DATA_PIN 3

CRGBArray<NUM_LEDS_CURRENT> leds;

uint8_t comBuffer[64];

enum msg {INCORRECT_OPEN_SEQUENCE, NO_DATA_FINISH_SYMBOL, WAITING_FOR_OPENING_SEQUENCE, OK_OPEN_SEQUENCE};

void show_msg(msg e){
    leds.fill_solid(CRGB::Black);
    bool halt = false;
    switch(e){
        case INCORRECT_OPEN_SEQUENCE:
            leds[0] = CRGB::Red;
            halt = true;
            break;
        case NO_DATA_FINISH_SYMBOL:
            leds[0] = CRGB::Blue;
            halt = true;
            break;
        case WAITING_FOR_OPENING_SEQUENCE:
            leds[0] = CRGB::Blue;
            leds[1] = CRGB::Blue;
            break;
        case OK_OPEN_SEQUENCE:
            leds[0] = CRGB::Green;
            leds[1] = CRGB::Green;
            break;
    }
    FastLED.show(); 

    // endless loop if unrecoverable error
    while(halt) 
      FastLED.delay(2000);
}

void setup() {
    // add leds
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS_CURRENT);
    
    // begin serial communication
    Serial.begin(115200);

    show_msg(WAITING_FOR_OPENING_SEQUENCE);

    // wait for start code
    while(!Serial.available());

    // check opening string
    if(Serial.readString() != "hello"){
       show_msg(INCORRECT_OPEN_SEQUENCE);
       Serial.write("unknown");
    }
    else {
        // respond
        Serial.write("SAM");
        show_msg(OK_OPEN_SEQUENCE);
    }
}

void loop() {
  if(Serial.available()){
    // read data for connected leds
    Serial.readBytes((char*)leds.leds, NUM_LEDS_CURRENT * 3);

    // acknowledge read
    Serial.write('k');
    FastLED.show();
    
  }
  
}
