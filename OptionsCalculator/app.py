from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException, Query, Depends
from .database import create_tables_and_db, get_session
from .models import Option, OptionRead, OptionCreate, OptionUpdate
from .PVCalculationEngine import OptionsCalculator
from typing import List
import logging

app = FastAPI()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def on_startup():
    create_tables_and_db()


# Create an option
@app.post("/options/", response_model=OptionRead)
def create_option(*, session: Session = Depends(get_session), option: OptionCreate):
    try:
        db_option = Option.from_orm(option)
        session.add(db_option)
        session.commit()
        session.refresh(db_option)
        logger.info(f"Option {db_option.name} with ID {db_option.id} created successfully")
        return db_option
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create option: {str(e)}")


# Get all options in database, with pagination limited to 100 results max.
@app.get("/options/", response_model=List[OptionRead])
def read_options(*, session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, lte=100)):
    try:
        options = session.exec(select(Option).offset(offset).limit(limit)).all()
        logger.info(f"Retrieved {len(options)} options from the database")
        return options
    except Exception as e:
        logger.error(f"Failed to retrieve options: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve options: {str(e)}")


# Get one singular option
@app.get("/options/{option_id}", response_model=OptionRead)
def read_option(*, session: Session = Depends(get_session), option_id: int):
    try:
        option = session.get(Option, option_id)
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        logger.info(f"Retrieved option with ID {option_id} from the database")
        return option
    except Exception as e:
        logger.error(f"Failed to retrieve option: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve option: {str(e)}")


# Update any of the option parameters
@app.patch("/options/{option_id}", response_model=OptionRead)
def update_option(*, session: Session = Depends(get_session), option_id: int, option: OptionUpdate):
    try:
        db_option = session.get(Option, option_id)
        if not db_option:
            raise HTTPException(status_code=404, detail="Option not found")
        option_data = option.dict(exclude_unset=True)  # include only values sent back by the client
        for key, value in option_data.items():
            setattr(db_option, key, value)
        session.add(db_option)
        session.commit()
        session.refresh(db_option)
        logger.info(f"Updated option with ID {option_id}")
        return db_option
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update option: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update option: {str(e)}")


# Delete an option by providing its ID
@app.delete("/options/{option_id}")
def delete_option(*, session: Session = Depends(get_session), option_id: int):
    try:
        option = session.get(Option, option_id)
        if not option:
            raise HTTPException(status_code=404, detail="Option not found")
        session.delete(option)
        session.commit()
        logger.info(f"Deleted option with ID {option_id}")
        return {"deleted": True}
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete option: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete option: {str(e)}")


# Calculate an options black 76 price and store it in database.
@app.patch("/options_black76/{option_id}", response_model=OptionRead)
def store_black76_price(*, session: Session = Depends(get_session), option_id: int):
    results = session.exec(select(Option).where(Option.id == option_id))
    option_data = results.one_or_none()
    if not option_data:
        raise HTTPException(status_code=404, detail="Option not found")
    if option_data.option_type.lower() == 'call' or option_data.option_type.lower() == 'put':
        black76_price = OptionsCalculator.calculate_price(float(option_data.strike),
                                                          float(option_data.time_to_maturity),
                                                          float(option_data.risk_free_rate),
                                                          float(option_data.volatility),
                                                          float(option_data.future_price),
                                                          str(option_data.option_type))
    else:
        raise HTTPException(status_code=422, detail="Invalid option type please enter 'call' or 'put'")

    option_data.black76_price = black76_price
    session.add(option_data)

    try:
        session.commit()
        session.refresh(option_data)
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error storing option price")
    logger.info(f"Option price calculated for option with ID {option_id} and added to database")
    return option_data
