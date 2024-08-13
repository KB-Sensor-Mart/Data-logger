import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';

const path = 'COM9'; // Replace with your actual serial port path
const baudRate = 115200;

const port = new SerialPort({
  path: path,
  baudRate: baudRate
});

const parser = port.pipe(new ReadlineParser({ delimiter: '\n' }));

port.on('error', function(err) {
  console.error('Error: ', err.message);
});

port.on('open', function() {
  console.log('Port opened successfully');

  // Send initial data once the port is opened
  port.write('Hello, FTDI232!\n', function(err) {
    if (err) {
      return console.error('Error on write: ', err.message);
    }
    console.log('Message written to serial port');
  });
});


// Flag to differentiate between original data and echoed data
let isEcho = false;


// Handle data received from the serial port
parser.on('data', function(data) {
  console.log('Received data: ', data);

  if (!isEcho) {
    isEcho = true;  // Set the flag to indicate this data will be echoed
    port.write(`Echo: ${data}\n`, function(err) {
      if (err) {
        return console.error('Error on write: ', err.message);
      }
      console.log('Echoed data back to serial port');
    });
  } else {
    isEcho = false;  // Reset the flag for the next incoming data
  }
});

