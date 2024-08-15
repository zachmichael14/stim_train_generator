#include <Arduino.h>
#include <hardware/pwm.h>

const int triggerPin = 27;
const char amplitudePin = 26;
const int ledPin = 25;

#define START_BYTE 0xAA
#define END_BYTE 0x55
#define ACK_BYTE 0x06
#define NAK_BYTE 0x15

#define CMD_SET_PARAMS 0x01

#define MAX_PACKET_SIZE 12

struct StimParams {
  uint8_t channel;
  uint16_t amplitude;
  float frequency;
};

StimParams currentParams = {0, 0, 0.0};

void setup() {
  pinMode(triggerPin, OUTPUT);
  pinMode(amplitudePin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);

   // Set up PWM for amplitude control
  // gpio_set_function(amplitudePin, GPIO_FUNC_PWM);
  // uint slice_num = pwm_gpio_to_slice_num(amplitudePin);
  // pwm_set_wrap(slice_num, 1023);  // 8-bit resolution
  // pwm_set_enabled(slice_num, true);

  for (int i = 1; i <= 8; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
}

void setAmplitude(uint16_t amp) {
    // Map amplitude from 0-1000 (mA) to 0-1023 (PWM range)
    uint16_t value = map(amp, 0, 1000, 0, 1023);
    analogWrite(amplitudePin, value);
    // pwm_set_gpio_level(amplitudePin, value);
}


void setChannel(uint8_t channel) {
  if (channel >= 1 && channel <= 8) {
    allChannelsOff();
    digitalWrite(channel, HIGH);
  }
}

void allChannelsOff() {
  for (int i = 1; i <= 8; i++) {
    digitalWrite(i, LOW);
  }
}

void trigger() {
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(1);
  digitalWrite(triggerPin, LOW);
}

void frequencyTrigger(float frequency) {
  if (frequency > 0) {
    float periodInMs = (1 / frequency) * 1000;
    trigger();
    delay(periodInMs);
  }
}

bool processPacket(uint8_t* packet, int packetSize) {
  if (packet[0] != START_BYTE || packet[packetSize-1] != END_BYTE) {
    return false;
  }

  // Verify checksum
  uint8_t calculatedChecksum = 0;
  for (int i = 0; i < packetSize - 2; i++) {  // Include START_BYTE, exclude checksum and END_BYTE
    calculatedChecksum ^= packet[i];
  }
  if (calculatedChecksum != packet[packetSize-2]) {
    return false;
  }

  uint8_t cmd = packet[1];
  uint8_t flags = packet[2];
  int index = 3;

  if (cmd == CMD_SET_PARAMS) {
    if (flags & 1) {  // Channel flag
      currentParams.channel = packet[index++];
      setChannel(currentParams.channel);
    }
    if (flags & 2) {  // Amplitude flag

      currentParams.amplitude = (packet[index+1] << 8) | packet[index];
      index += 2;
      setAmplitude(currentParams.amplitude);
    }
    if (flags & 4) {  // Frequency flag
      memcpy(&currentParams.frequency, &packet[index], sizeof(float));
      index += 4;
    }
  } else {
    return false;
  }

  return true;
}

void loop() {
  static uint8_t packetBuffer[MAX_PACKET_SIZE];
  static int packetIndex = 0;
  static bool inPacket = false;

  while (Serial.available() > 0) {
    uint8_t inByte = Serial.read();

    if (!inPacket && inByte == START_BYTE) {
      inPacket = true;
      packetIndex = 0;
    }

    if (inPacket) {
      packetBuffer[packetIndex++] = inByte;

      if (inByte == END_BYTE || packetIndex == MAX_PACKET_SIZE) {
        bool success = processPacket(packetBuffer, packetIndex);
        Serial.write(success ? ACK_BYTE : NAK_BYTE);
        inPacket = false;
        packetIndex = 0;

        if (success) {
          digitalWrite(ledPin, HIGH);
          delay(50);
          digitalWrite(ledPin, LOW);
        }
      }
    }
  }

  // Apply stimulation based on current parameters
  if (currentParams.frequency > 0) {
    frequencyTrigger(currentParams.frequency);
  }
}