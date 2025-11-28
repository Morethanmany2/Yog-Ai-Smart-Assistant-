// ==============================
// ESP32 - 8x6 Pressure Matrix
// Two 16-channel multiplexers
// Clean CSV output: 48 values + END
// ==============================

// -------- MUX A (Column Read) Pins ----------
const byte s0 = 21;
const byte s1 = 19;
const byte s2 = 18;
const byte s3 = 5;

// -------- MUX B (Row Select) Pins -----------
const byte w0 = 23;
const byte w1 = 22;
const byte w2 = 27;
const byte w3 = 26;

// -------- Analog input pin ------------------
const byte SIG_PIN = 32;  // Must be ADC1 pin on ESP32

// -------- Matrix Layout ---------------------
byte rowChannels[8] = {0, 1, 2, 3, 4, 5, 6, 7};         // 8 rows
byte colChannels[6] = {10, 11, 12, 13, 14, 15};         // 6 columns

// -------- MUX Truth Table -------------------
const boolean muxChannel[16][4] = {
  {0,0,0,0}, {1,0,0,0}, {0,1,0,0}, {1,1,0,0},
  {0,0,1,0}, {1,0,1,0}, {0,1,1,0}, {1,1,1,0},
  {0,0,0,1}, {1,0,0,1}, {0,1,0,1}, {1,1,0,1},
  {0,0,1,1}, {1,0,1,1}, {0,1,1,1}, {1,1,1,1}
};

// ==============================
// SELECT MUX A = columns
// ==============================
void setMuxA(byte ch) {
  digitalWrite(s0, muxChannel[ch][0]);
  digitalWrite(s1, muxChannel[ch][1]);
  digitalWrite(s2, muxChannel[ch][2]);
  digitalWrite(s3, muxChannel[ch][3]);
  delayMicroseconds(80);
}

// ==============================
// SELECT MUX B = rows
// ==============================
void setMuxB(byte ch) {
  digitalWrite(w0, muxChannel[ch][0]);
  digitalWrite(w1, muxChannel[ch][1]);
  digitalWrite(w2, muxChannel[ch][2]);
  digitalWrite(w3, muxChannel[ch][3]);
  delayMicroseconds(80);
}

// ==============================
// SETUP
// ==============================
void setup() {

  Serial.begin(115200);

  pinMode(s0, OUTPUT); pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT); pinMode(s3, OUTPUT);

  pinMode(w0, OUTPUT); pinMode(w1, OUTPUT);
  pinMode(w2, OUTPUT); pinMode(w3, OUTPUT);

  pinMode(SIG_PIN, INPUT);

  Serial.println("8x6 Matrix Initialized");
}

// ==============================
// LOOP: READ MATRIX
// ==============================
void loop() {

  // Loop rows
  for (int r = 0; r < 8; r++) {
    setMuxB(rowChannels[r]);

    // Loop columns
    for (int c = 0; c < 6; c++) {
      setMuxA(colChannels[c]);

      int raw = analogRead(SIG_PIN);

      // Output value + comma
      Serial.print(raw);

      // Comma for all except last value
      if (!(r == 7 && c == 5)) Serial.print(",");
    }
  }

  // End-of-frame marker
  Serial.println("END");

  delay(30);  // ~33 FPS
}
