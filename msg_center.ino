#include <SoftwareSerial.h>
#include <stdlib.h>

int msgcenter_buff_int;
int msgcenter_byte_num = 4;

char msgcenter_buff_char[] = {
  ' ', ' ', ' ', ' '
};

SoftwareSerial fpga_serial(8, 9);

int fpga_buff_int = 0;

void wait_msgcenter_connection() {

  while (!Serial.available()) {}
}

void read_msgcenter_serial() {

  wait_msgcenter_connection();

  Serial.readBytes(
    msgcenter_buff_char,
    msgcenter_byte_num
  );
}

void fulfill_with_zeros(int n_zeros) {

  for (int idx = 0; idx < n_zeros; idx++) {
    Serial.write('0');
  }
}

void write_msgcenter_serial() {

  if (msgcenter_buff_int == 0) {
    fulfill_with_zeros(4);
  }
  else if (msgcenter_buff_int < 10) {
    fulfill_with_zeros(3);
  }
  else if (msgcenter_buff_int < 100) {
    fulfill_with_zeros(2);
  }
  else if (msgcenter_buff_int < 1000) {
    fulfill_with_zeros(1);
  }

  Serial.print(msgcenter_buff_int);
}

void clear_msgcenter_buffer() {

  msgcenter_buff_char[0] = (char)0;
}

void msgcenter_buffer_to_int() {

  msgcenter_buff_int = atoi(msgcenter_buff_char);
}

void msgcenter_buffer_to_char() {

  clear_msgcenter_buffer();

  itoa(
    msgcenter_buff_int,
    msgcenter_buff_char,
    10
  );
}

void wait_fpga_connection() {

  while (!fpga_serial.available()) {}
}

void clear_fpga_buffer() {

  fpga_buff_int = 0;
}

void read_fpga_serial() {

  wait_fpga_connection();

  clear_fpga_buffer();

  fpga_buff_int = fpga_serial.read();
}

void write_fpga_serial() {

  fpga_serial.write(fpga_buff_int);
}

void copy_buffer_fpga_to_msgcenter() {

  msgcenter_buff_int = fpga_buff_int;
}

void copy_buffer_msgcenter_to_fpga() {

  fpga_buff_int = msgcenter_buff_int;
}

void setup() {

  Serial.begin(9600);

  fpga_serial.begin(115200);
}

void loop() {

  bool fpga = fpga_serial.available();

  bool msgcenter = Serial.available();

  if (msgcenter) {

    read_msgcenter_serial();

    msgcenter_buffer_to_int();

    copy_buffer_msgcenter_to_fpga();

    write_fpga_serial();
  }

  else if (fpga) {

    read_fpga_serial();

    copy_buffer_fpga_to_msgcenter();

    msgcenter_buffer_to_char();

    write_msgcenter_serial();
  }

  else {

    clear_fpga_buffer();

    clear_msgcenter_buffer();
  }
}