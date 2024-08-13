// controllers/authController.js

const jwt = require('jsonwebtoken');
const userModel = require('../models/usermodel');

const login = (req, res) => {
  const { email, password } = req.body;

  userModel.findUserByCredentials(email, password, (err, data) => {
    if (err) {
      console.error("Error querying MySQL:", err);
      return res.json({ Message: "Server side error" });
    }
    if (data.length > 0) {
      const name = data[0].name;
      const token = jwt.sign({ name }, process.env.JWT_SECRET || "our-password", { expiresIn: '1d' });

      res.cookie('token', token, { httpOnly: true, secure: true });
      return res.json({ status: "success" });
    } else {
      return res.json({ Message: "No record found" });
    }
  });
};

module.exports = {
  login,
};
