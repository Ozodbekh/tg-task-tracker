from getpass import getpass

from app.core.security import PasswordHasher


def main() -> None:
    password = getpass("Password: ")
    if password != getpass("Repeat password: "):
        raise SystemExit("Passwords do not match")
    print(PasswordHasher.hash(password))


if __name__ == "__main__":
    main()
