from pydantic import BaseModel


class Name(BaseModel):
    firstName: str
    lastName: str


class FirstName(BaseModel):
    firstName: str


class LastName(BaseModel):
    lastName: str
