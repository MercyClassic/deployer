import json
import os

from cryptography.fernet import Fernet
from sqlalchemy import Text, TypeDecorator


class EncryptedString(TypeDecorator):
    impl = Text
    cache_ok = True
    key = os.environ['ENCRYPTION_KEY']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = Fernet(key=self.key)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return self.cipher.encrypt(json.dumps(value).encode()).decode('utf-8')
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(
                self.cipher.decrypt(value.encode('utf-8')).decode('utf-8'),
            )
        return value


class EncryptedWithToDictMethod(EncryptedString):
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if hasattr(value, 'to_dict'):
            return super().process_bind_param(value.to_dict(), dialect)
        return super().process_bind_param(value, dialect)
