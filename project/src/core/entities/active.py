from pydantic import BaseModel


class Active(BaseModel):
    is_active: bool
