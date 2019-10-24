'use strict';

// Winston Logger - Configuration file

const { createLogger, format, transports } = require('winston');
const { combine, timestamp, label, printf, prettyPrint, json } = format;

const myFormat = printf(info => {
  return `${info.timestamp} ${info.level}: ${info.message}`;
});


export const Logger = createLogger({
 level: 'debug',
// level: 'info',
format: combine(
    timestamp(),
    json()
  ),
  transports: [
    //
    // - Write to all logs with level `info` and below to `combined.log` 
    // - Write all logs error (and below) to `error.log`.
    //
//    new transports.Console(),
    new transports.File({ filename: 'violation.log', level: 'warn', json: true }),
    new transports.File({ filename: 'error.log', level: 'error', json: true }),
    new transports.File({ filename: 'combined.log', json: true })
  ]
});