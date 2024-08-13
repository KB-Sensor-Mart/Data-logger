const express = require('express');
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');
const cookieParser = require('cookie-parser');
const authRoutes = require('./routes/authroutes');

const port = process.env.PORT || 5001;
const app = express();

app.use(express.json());
app.use(cookieParser());

const corsOptions = {
  origin: ["http://localhost:3000"],
  methods: ["GET", "POST"],
  credentials: true
};

app.use(cors(corsOptions));

// Use the routes
app.use('/api/auth', authRoutes);

const httpServer = http.createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*',
  },
});

httpServer.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
