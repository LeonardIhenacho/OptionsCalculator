from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import condecimal, validator
from datetime import datetime


class OptionsBase(SQLModel):
    """Base Datamodel representation for Options"""
    name: str = Field(index=True)
    strike: condecimal(max_digits=7, decimal_places=3)
    time_to_maturity: condecimal(max_digits=6, decimal_places=3)
    risk_free_rate: condecimal(max_digits=6, decimal_places=3)
    volatility: condecimal(max_digits=6, decimal_places=3)
    future_price: condecimal(max_digits=7, decimal_places=3)
    option_type: str
    black76_price: Optional[condecimal(max_digits=7, decimal_places=3)] = None

    @validator('option_type')
    def type_must_be_call_or_put(cls, value):
        if value.lower() not in {'call', 'put'}:
            raise ValueError('Option type must be either "call" or "put"')
        return value.lower()


class Option(OptionsBase, table=True):  # This is the table model
    id: Optional[int] = Field(default=None, primary_key=True)


class OptionCreate(OptionsBase):
    pass


class OptionRead(OptionsBase):
    id: int


class OptionUpdate(SQLModel):
    name: Optional[str] = None
    strike: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    time_to_maturity: Optional[condecimal(max_digits=6, decimal_places=3)] = None
    risk_free_rate: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    volatility: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    future_price: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    option_type: Optional[str] = None
    black76_price: Optional[condecimal(max_digits=7, decimal_places=3)] = None

    class config:
        orm_mode = True
