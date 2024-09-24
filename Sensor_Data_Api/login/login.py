import mariadb
from login.dbconfig import db_config


class AuthService:
    def __init__(self, db_config):
        self.db_config = db_config

    # Use synchronous MariaDB connection
    def _get_connection(self):
        try:
            connection = mariadb.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database=self.db_config["database"],
            )
            if connection is None:
                raise Exception("Failed to establish a database connection")
            print("Connection established:", connection)  # Debugging line
            return connection
        except Exception as e:
            print(f"Database connection failed: {e}")  # Log the exact error
            raise Exception(f"Database connection failed: {e}")

    def login(self, username: str, password: str) -> (bool, str):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            print("Cursor created:", cursor)  # Debugging line

            if cursor is None:
                raise Exception("Cursor creation failed")

            # Execute the query using the synchronous cursor
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            connection.close()

            if user:
                return True, "Login successful"
            return False, "Invalid username or password"
        except Exception as e:
            print(f"Login failed: {e}")
            return False, f"Login failed: {e}"

    def reset_password(self, username: str, new_password: str) -> (bool, str):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if not user:
                connection.close()
                return False, "User not found"

            # Update the password
            cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_password, username))
            connection.commit()
            connection.close()

            return True, "Password reset successful"
        except Exception as e:
            print(f"Password reset failed: {e}")
            return False, f"Password reset failed: {e}"


# Instantiate the auth service using db_config
auth_service = AuthService(db_config=db_config)