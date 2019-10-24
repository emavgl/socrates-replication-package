// grab the packages we need
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const uuidv4 = require('uuid/v4');
const path = require('path');
const spawn = require('child_process').spawn;

var app = express();
const server = require('http').Server(app);
const io = require('socket.io')(server);

app.use(cors({origin: '*'}));
app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
app.use(express.static(path.join(__dirname, 'logs')));

server.listen(5004);

// routes will go here
app.post('/test', function(req, res) {
    let contractName = req.body.contractName;
    let contractCode = req.body.contractCode;
    let filename = "./codes/" + contractName + '.sol';
    fs.writeFile(filename, contractCode, (err) => {  
        if (err) throw err;
        res.send(uuidv4());
    });
});

function execTest(name, token, socket){
    
    console.log("Executing", name);
    console.log("Token", token);

    var myProcess = spawn('bash', [ 'runTest.sh', name, token ]);
    myProcess.stdout.setEncoding('utf-8');
    myProcess.stdout.on('data', function (data) {
        socket.emit('stdout', data);
    });

    myProcess.stderr.setEncoding('utf-8');
    myProcess.stderr.on('data', function (data) {
        socket.emit('stdout', data);
    });

    myProcess.on("close", function() {
        socket.emit('end');
    });
}

io.on('connection', function (socket) {
    let token = socket.handshake.query.token;
    let name = socket.handshake.query.name;
    execTest(name, token, socket);
});

console.log('Server started! At http://localhost:' + 5004);

