#include <Wire.h>
#include <ESP8266WiFi.h>
#include "Protocentral_MAX30205.h"
#include <protocentral_TLA20xx.h>
#include <MAX3010x.h>
#include "filters.h"

#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

// WiFi credentials
const char* ssid = "Karthi";
const char* password = "karthi11";

// Google Apps Script Web App URL
const String scriptURL = "https://script.google.com/macros/s/AKfycbxCc2gQcyq1IhcL8rWeoDhL7Cg3nHDWiolE6zQP7uor4O-1SeWvIJy-XEyR9w1TxZVHXQ/exec";

// Temperature Sensor
MAX30205 tempSensor;

// GSR Sensor (TLA2022)
#define TLA20XX_I2C_ADDR 0x49
TLA20XX tla2022(TLA20XX_I2C_ADDR);

// Heart Rate Sensor (MAX30105)
MAX30105 sensor;
const auto kSamplingRate = sensor.SAMPLING_RATE_400SPS;
const float kSamplingFrequency = 400.0;

// Filters
const float kLowPassCutoff = 5.0;
const float kHighPassCutoff = 0.5;
const bool kEnableAveraging = false;
const int kAveragingSamples = 50;

HighPassFilter high_pass_filter(kHighPassCutoff, kSamplingFrequency);
LowPassFilter low_pass_filter(kLowPassCutoff, kSamplingFrequency);
Differentiator differentiator(kSamplingFrequency);
MovingAverageFilter<kAveragingSamples> averager;

// Finger Detection
const unsigned long kFingerThreshold = 10000;
const unsigned int kFingerCooldownMs = 500;
const float kEdgeThreshold = -2000.0;
long last_heartbeat = 0;
long finger_timestamp = 0;
bool finger_detected = false;
float last_diff = NAN;
bool crossed = false;
long crossed_time = 0;

void setup() {
    Serial.begin(9600);
    Wire.begin();

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");

    // Initialize temperature sensor
    unsigned long startTime = millis();
    while (!tempSensor.scanAvailableSensors()) {
        if (millis() - startTime > 10000) {
            Serial.println("Timeout: Couldn't find temperature sensor.");
            break;
        }
        Serial.println("Waiting for temperature sensor...");
        delay(500);
    }
    tempSensor.begin();

    // Initialize heart rate sensor
    if (sensor.begin() && sensor.setSamplingRate(kSamplingRate)) {
        Serial.println("Heart rate sensor initialized");
    } else {
        Serial.println("Heart rate sensor not found!");
    }

    // Initialize GSR sensor
    tla2022.begin();
    tla2022.setMode(TLA20XX::OP_CONTINUOUS);
    tla2022.setDR(TLA20XX::DR_128SPS);
    tla2022.setFSR(TLA20XX::FSR_2_048V);

    Serial.println("Sensors initialized!");
}

void loop() {
    // Read temperature
    float temperature = tempSensor.getTemperature();
    Serial.print("Temperature: ");
    Serial.print(temperature, 4);
    Serial.println(" 'C");

    // Read raw GSR value and voltage
    float raw_value = tla2022.read_adc();
    float gsr_voltage = raw_value * (2.048 / 32768.0);
    Serial.print("Raw value: ");
    Serial.println(raw_value*87);
    Serial.print("GSR Voltage: ");
    Serial.print(gsr_voltage, 6);
    Serial.println(" V");

    // Read from heart sensor (optional, not uploaded)
    auto sample = sensor.readSample(1000);
    float current_value = sample.red;

    // Process heart rate (optional for display only)
    if (sample.red > kFingerThreshold) {
        if (millis() - finger_timestamp > kFingerCooldownMs) {
            finger_detected = true;
        }
    } else {
        differentiator.reset();
        averager.reset();
        low_pass_filter.reset();
        high_pass_filter.reset();
        finger_detected = false;
        finger_timestamp = millis();
    }

    if (finger_detected) {
        current_value = low_pass_filter.process(current_value);
        current_value = high_pass_filter.process(current_value);
        float current_diff = differentiator.process(current_value);

        if (!isnan(current_diff) && !isnan(last_diff)) {
            if (last_diff > 0 && current_diff < 0) {
                crossed = true;
                crossed_time = millis();
            }
            if (current_diff > 0) {
                crossed = false;
            }
            if (crossed && current_diff < kEdgeThreshold) {
                if (last_heartbeat != 0 && crossed_time - last_heartbeat > 300) {
                    int bpm = 60000 / (crossed_time - last_heartbeat);
                    if (bpm > 50 && bpm < 250) {
                        Serial.print("Heart Rate (bpm): ");
                        Serial.println(bpm);
                    }
                }
                crossed = false;
                last_heartbeat = crossed_time;
            }
        }
        last_diff = current_diff;
    }

    // Upload raw value, GSR voltage, and temperature
    sendToGoogleSheet(raw_value, gsr_voltage, temperature);

    delay(100);  // small delay
}

void sendToGoogleSheet(float rawVal, float gsrVolt, float tempVal) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        WiFiClientSecure client;
        client.setInsecure();  // Disable SSL verification

        String url = scriptURL + "?raw=" + String(rawVal*87, 2)
                                 + "&gsrvoltage=" + String(gsrVolt, 6)
                                 + "&temp=" + String(tempVal, 4);
        http.begin(client, url);
        int httpCode = http.GET();

        if (httpCode == HTTP_CODE_OK) {
            Serial.println(" Data uploaded successfully.");
        } else {
            Serial.print(" Upload failed. HTTP code: ");
            Serial.println(httpCode);
        }

        http.end();
    } else {
        Serial.println(" WiFi not connected. Skipping upload.");
    }
}
