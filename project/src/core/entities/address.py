from pydantic import BaseModel


class Address(BaseModel):
    full_address: str
