#include <FastLED.h>

#define NUM_LEDS_CURRENT 80//160
#define DATA_PIN 6

CRGBArray<NUM_LEDS_CURRENT> leds;

uint8_t comBuffer[64];

enum msg {INCORRECT_OPEN_SEQUENCE, INITIAL, WAITING_FOR_OPENING_SEQUENCE, WAIT_FOR_SERIAL, OK_OPEN_SEQUENCE};

void show_msg(msg e){
    leds.fill_solid(CRGB::Black);
    bool halt = false;
    switch(e){
        case INCORRECT_OPEN_SEQUENCE:
            leds[0] = CRGB::Red;
            leds[1] = CRGB::Red;
            halt = true;
            break;
        case INITIAL:
            leds[0] = CRGB::Blue;
            break;
        case WAIT_FOR_SERIAL:
            leds[0] = CRGB::Blue;
            leds[1] = CRGB::Blue;
            break;
        case WAITING_FOR_OPENING_SEQUENCE:
            leds[0] = CRGB::Blue;
            leds[1] = CRGB::Blue;
            leds[2] = CRGB::Blue;
            break;
        case OK_OPEN_SEQUENCE:
            leds[0] = CRGB::Green;
            leds[1] = CRGB::Green;
            break;
    }
    FastLED.show(); 
    FastLED.delay(2000);
}

void setup() {
    show_msg(INITIAL);
    // add leds
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS_CURRENT);
    
    // begin serial communication
    Serial.begin(115200);

    show_msg(WAIT_FOR_SERIAL);

    // wait for start code
    while(!Serial.available());

    show_msg(WAITING_FOR_OPENING_SEQUENCE);
    
    // check opening string
    while(Serial.readString() != "hello"){
       show_msg(INCORRECT_OPEN_SEQUENCE);
       Serial.write("INCORRECT_OPEN_SEQUENCE");
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
