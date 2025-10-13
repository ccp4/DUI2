import hashlib, secrets, getpass
import os, json
from datetime import datetime

class AuthSystem:
    def __init__(self, filename = "users_data.json"):
        self.filename = filename
        self.users = self.load_data()
        self.tokens = {}  # token -> username

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        print("self.users =", self.users)
        with open(self.filename, 'w') as usr_dat:
            json.dump(self.users, usr_dat)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password):
        if username in self.users:
            return False, "Username already exists"

        password_hash = self.hash_password(password)
        self.users[username] = {
            'password_hash': password_hash,
            'created_at': datetime.now().isoformat()
        }
        self.save_data()
        return True, "User created successfully"

    def login(self, username, password):
        if username not in self.users:
            return False, "User does not exist"

        password_hash = self.hash_password(password)
        if self.users[username]['password_hash'] != password_hash:
            return False, "Invalid password"

        token = str(secrets.token_hex(16))

        self.tokens[token] = username
        return True, token

    def validate(self, token):
        username = self.tokens.get(token)
        if username:
            return True, "Validated user " + username

        return False, "Invalid token"

    def logout(self, token):
        if token in self.tokens:
            del self.tokens[token]
            return True, "Logged out successfully"

        return False, "Invalid token"

    def _list_users(self):
        # only used for testing consider removing
        return list(self.users.keys())

    def _list_tokens(self):
        # only used for testing consider removing
        return self.tokens.copy()

def main():
    auth = AuthSystem()
    print("=== Simple Authentication System ===")
    print("Commands: register, login, validate, logout, users, tokens, quit")
    try:
        while True:
            command = input("\nEnter command: ").strip().lower()

            if command == 'register':
                username = input("Username: ").strip()
                password = getpass.getpass("Password: ")
                success, message = auth.create_user(username, password)
                print(f"Result: {message}")

            elif command == 'login':
                username = input("Username: ").strip()
                password = getpass.getpass("Password: ")
                success, message = auth.login(username, password)
                if success:
                    print(f"Login successful! Your token: {message}")

                else:
                    print(f"Login failed: {message}")

            elif command == 'validate':
                token = input("Token: ").strip()
                success, message = auth.validate(token)
                print(f"success: {success}")
                print(f"Result: {message}")

            elif command == 'logout':
                token = input("Token: ").strip()
                success, message = auth.logout(token)
                print(f"success: {success}")
                print(f"Result: {message}")

            elif command == 'users':
                # for testing only, consider removing
                users = auth._list_users()
                print(f"Registered users: {users}")

            elif command == 'tokens':
                # for testing only, consider removing
                tokens = auth._list_tokens()
                print("Active tokens:")
                for token, username in tokens.items():
                    print(f"  {username}: {token[:16]}...")

            elif command in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            else:
                print("Unknown command. Available: register, login, validate, logout, users, tokens, quit")

    except KeyboardInterrupt:
        print(" Keyboard Interrupt ")

    except EOFError:
        print("EOF Error")


if __name__ == "__main__":
    main()
