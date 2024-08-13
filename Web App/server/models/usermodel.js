const db = require('../config/db');

const findUserByCredentials = (username, password, callback) => {
  const sql = "SELECT * FROM loginuser WHERE user_name = ? AND user_pass = ?";
  db.query(sql, [username, password], (err, results) => {
    if (err) return callback(err, null);
    return callback(null, results);
  });
};

module.exports = {
  findUserByCredentials,
};
