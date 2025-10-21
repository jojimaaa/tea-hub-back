import bcrypt

def get_password_hash(password: str) -> str:
    # bcrypt aceita no máximo 72 bytes
    safe_password = password[:72].encode('utf-8')
    hashed = bcrypt.hashpw(safe_password, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))