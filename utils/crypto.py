from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.CRYPTO_KEY)

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str | None) -> str:
    if not token:
        return ""
    return fernet.decrypt(token.encode()).decode()
