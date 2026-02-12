#!/usr/bin/env python3
"""비밀번호 해시 생성 스크립트"""
import bcrypt
import secrets

def hash_password(password: str) -> str:
    """bcrypt로 비밀번호 해싱"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def generate_secret_key(length: int = 64) -> str:
    """안전한 랜덤 시크릿 키 생성"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    password = "theoddl11!"
    hashed = hash_password(password)
    secret_key = generate_secret_key()

    print("=== 생성된 보안 정보 ===\n")
    print(f"원본 비밀번호: {password}")
    print(f"해시된 비밀번호:\n{hashed}\n")
    print(f"새 SESSION_SECRET_KEY:\n{secret_key}\n")
    print("=== .env에 추가하세요 ===")
    print(f'ADMIN_PASSWORD_HASH="{hashed}"')
    print(f'SESSION_SECRET_KEY="{secret_key}"')
