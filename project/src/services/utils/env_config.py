from decouple import AutoConfig

config = AutoConfig(".env")

__all__ = [config]
