from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException, Query, Depends
from .database import create_tables_and_db, get_session
from .models import Option, OptionRead, OptionCreate, OptionUpdate
from .PVCalculationEngine import OptionsCalculator
from typing import List

app = FastAPI()


# Create the required tables and databases once application starts running
@app.on_event("startup")
def on_startup():
    create_tables_and_db()


# Create an option
@app.post("/options/", response_model=OptionRead)
def create_option(*, session: Session = Depends(get_session), option: OptionCreate):
    db_option = Option.from_orm(option)
    session.add(db_option)
    session.commit()
    session.refresh(db_option)
    return db_option


# Get all options in database, with pagination limited to 100 results max.
@app.get("/options/", response_model=List[OptionRead])
def read_options(*, session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, lte=100)):
    options = session.exec(select(Option).offset(offset).limit(limit)).all()
    return options


# Get one singular option
@app.get("/options/{option_id}", response_model=OptionRead)
def read_option(*, session: Session = Depends(get_session), option_id: int):
    option = session.get(Option, option_id)
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    return option


# Update any of the option parameters
@app.patch("/options/{option_id}", response_model=OptionRead)
def update_option(*, session: Session = Depends(get_session), option_id: int, option: OptionUpdate):
    db_option = session.get(Option, option_id)
    if not db_option:
        raise HTTPException(status_code=404, detail="Option not found")
    option_data = option.dict(exclude_unset=True)  # include only values sent back by the client
    for key, value in option_data.items():
        setattr(db_option, key, value)
    session.add(db_option)
    session.commit()
    session.refresh(option)
    return option


# Delete an option by providing its ID
@app.delete("/options/{option_id}")
def delete_option(*, session: Session = Depends(get_session), option_id: int):
    option = session.get(Option, option_id)
    if not option:
        raise HTTPException(status_code=404, detail="Option not found")
    session.delete(option)
    session.commit()
    return {"deleted": True}


# Calculate an options black 76 price and store it in database.
@app.patch("/options_black76/{option_id}", response_model=OptionRead)
def store_black76_price(*, session: Session = Depends(get_session), option_id: int):
    results = session.exec(select(Option).where(Option.id == option_id))
    option_data = results.one()
    if not option_data:
        raise HTTPException(status_code=404, detail="Option not found")
    if option_data.option_type == 'call':
        black76_price = OptionsCalculator.Call(float(option_data.strike), float(option_data.maturity),
                                               float(option_data.risk_free_rate),
                                               float(option_data.volatility), float(option_data.future_price))
    elif option_data.option_type == 'put':
        black76_price = OptionsCalculator.Put(float(option_data.strike), float(option_data.maturity),
                                              float(option_data.risk_free_rate),
                                              float(option_data.volatility), float(option_data.future_price))
    option_data.black76_price = black76_price
    session.add(option_data)
    session.commit()
    session.refresh(option_data)
    return option_data
