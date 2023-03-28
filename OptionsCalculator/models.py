from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import condecimal


class OptionsBase(SQLModel):
    """Base Datamodel representation for Options"""
    name: str = Field(index=True)
    strike: condecimal(max_digits=7, decimal_places=3)
    maturity: condecimal(max_digits=6, decimal_places=3)
    risk_free_rate: condecimal(max_digits=6, decimal_places=3)
    volatility: condecimal(max_digits=6, decimal_places=3)
    future_price: condecimal(max_digits=7, decimal_places=3)
    option_type: str
    black76_price: Optional[condecimal(max_digits=7, decimal_places=3)]


class Option(OptionsBase, table=True):  # This is the table model
    id: Optional[int] = Field(default=None, primary_key=True)


class OptionCreate(OptionsBase):
    pass


class OptionRead(OptionsBase):
    id: int


class OptionUpdate(SQLModel):
    name: Optional[str] = None
    strike: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    maturity: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    risk_free_rate: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    volatility: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    future_price: Optional[condecimal(max_digits=7, decimal_places=3)] = None
    option_type: Optional[str] = None
    black76_price: Optional[condecimal(max_digits=7, decimal_places=3)]
