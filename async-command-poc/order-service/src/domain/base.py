from decimal import Decimal

from pydantic import BaseModel


class Base(BaseModel):
    class Config:
        # Ensure Decimals are serialized as floats
        json_encoders = {
            Decimal: float
        }