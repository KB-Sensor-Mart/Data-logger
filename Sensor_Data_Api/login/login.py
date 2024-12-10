import mariadb
from login.dbconfig import db_config
from logging_config import get_logger
import uuid
from datetime import datetime, timedelta
import bcrypt

logger = get_logger(__name__)


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
            logger.info("Database connection established")
            return connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")  # Log the exact error
            raise Exception(f"Database connection failed: {e}")

    def login(self, username: str, password: str) -> (bool, str, str):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            # Fetch user details
            cursor.execute("SELECT id, password FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                session_key= str(uuid.uuid4())  # Generate session key
                expiry_time = datetime.now() + timedelta(hours=12)

                logger.info(f"Login successful for user: {username}")
                return True, "Login successful", session_key ,expiry_time # Return session key directly

            logger.warning("Login failed: Invalid username or password")
            return False, "Invalid username or password", None, None
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False, f"Login failed: {e}", None, None
        finally:
            connection.close()
            
    def validate_session(self, session_key: str) -> bool:
        try:
            codnnection = self._get_connection()
            cursor = connection.cursor()

            # Check session validity
            cursor.execute(
                "SELECT user_id, expires_at FROM sessions WHERE session_key=%s",
                (session_key,)
            )
            session = cursor.fetchone()

            if session:
                session_expiry = session[1]
                if datetime.now() < session_expiry:
                    return True  # Session is valid

            logger.warning("Session validation failed: Invalid or expired session")
            return False
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return False
        finally:
            connection.close()
            
    def logout(self, session_key: str) -> (bool, str):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            # Delete session
            cursor.execute("DELETE FROM sessions WHERE session_key=%s", (session_key,))
            connection.commit()
            logger.info("Logout successful")
            return True, "Logout successful"
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False, f"Logout failed: {e}"
        finally:
            connection.close()

    def reset_password(self, username: str, new_password: str) -> (bool, str):
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if not user:
                logger.warning("Password reset failed: User not found")
                return False, "User not found"

            # Update password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "UPDATE users SET password=%s WHERE username=%s",
                (hashed_password.decode('utf-8'), username),
            )
            connection.commit()
            logger.info(f"Password reset successful for user: {username}")
            return True, "Password reset successful"
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return False, f"Password reset failed: {e}"
        finally:
            connection.close()

# Instantiate the auth service using db_config
auth_service = AuthService(db_config=db_config)
