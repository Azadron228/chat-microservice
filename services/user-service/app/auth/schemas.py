from pydantic import BaseModel
from typing import Optional, Union

class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    preferred_username: Optional[str] = None
    exp: int
    iat: int
    aud: Union[str, list]