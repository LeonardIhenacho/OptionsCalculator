# Options Calculator API

This code implements a FastAPI application that exposes an API for managing financial options. It uses the SQLModel library to interact with a database, and the PVCalculationEngine module to calculate Black76 option prices.

The API has endpoints for creating, reading, updating, and deleting options, as well as for calculating the Black76 price of an option and storing it in the database.

The API also includes pagination functionality for retrieving options from the database in batches.

To use this code, you'll need to have SQLModel, FastAPI, and the PVCalculationEngine module installed. The database connection details will also need to be configured.


The main components of the project are:

* app.py: The main file that runs the FastAPI application and includes the endpoints for managing options and calculating the Black 76 price.


* database.py: Contains functions for creating the database and tables, as well as a function for getting a session to interact with the database.


* models.py: Defines the data models for the options, including input and output models for the API endpoints.


* PVCalculationEngine.py: Contains the custom calculation engine for Black 76 pricing.


* requirements.txt: The list of required packages to install the project's dependencies.

## Installation
* Clone the repository to your local machine
* Install dependencies using pip install -r requirements.txt
* Run the application using uvicorn OptionsCalculator.app:app --reload

##Usage
The API runs on http://localhost:8000/ and provides the following endpoints:

###Create an Option
* Endpoint: POST /options/
* Request Body: JSON with the following fields:
  * name: the name of the option
  * option_type: the type of the option, either "call" or "put"
  * strike: the strike price of the option
  * time_to_maturity: the time to maturity of the option
  * risk_free_rate: the risk-free rate used to calculate the option price
  * volatility: the volatility used to calculate the option price
  * future_price: the future price used to calculate the option price 
* Response Body: JSON with the same fields as the request body, as well as an id field assigned by the database


###Get all Options
* Endpoint: GET /options/
* Query Parameters:
  * offset: the number of records to skip before starting to return records (default: 0)
  * limit: the maximum number of records to return (default: 100, maximum: 100)
  * Response Body: JSON array of option objects with the following fields:
  * id: the unique identifier of the option
  * name: the name of the option
  * option_type: the type of the option, either "call" or "put"
  * strike: the strike price of the option
  * time_to_maturity: the time to maturity of the option
  * risk_free_rate: the risk-free rate used to calculate the option price
  * volatility: the volatility used to calculate the option price
  * future_price: the future price used to calculate the option price
  * black76_price: the Black 76 price of the option, if calculated
  
###Get one Option
* Endpoint: GET /options/{option_id}
* Path Parameters:
  * option_id: the unique identifier of the option
* Response Body: JSON object with the following fields:
    * id: the unique identifier of the option
    * name: the name of the option
    * option_type: the type of the option, either "call" or "put"
    * strike: the strike price of the option
    * time_to_maturity: the time to maturity of the option
    * risk_free_rate: the risk-free rate used to calculate the option price
    * volatility: the volatility used to calculate the option price
    * future_price: the future price used to calculate the option price
    * black76_price: the Black 76 price of the option, if calculated


###Update an Option
* Endpoint: PATCH /options/{option_id}
* Request Body: JSON with the following fields: { "field you wish to update": "new_value"}
  * Response Body: JSON array of option objects with the following fields:
  * id: the unique identifier of the option
  * name: the name of the option
  * option_type: the type of the option, either "call" or "put"
  * strike: the strike price of the option
  * time_to_maturity: the time to maturity of the option
  * risk_free_rate: the risk-free rate used to calculate the option price
  * volatility: the volatility used to calculate the option price
  * future_price: the future price used to calculate the option price
  * black76_price: the Black 76 price of the option (if calculated) 


###Delete an Option
* Endpoint: DELETE /options/{option_id}
* Response Body {deleted: true}




###Calculate the Black76 Price of an Option
* Endpoint: PATCH /options_black76/{option_id}
  * Response Body: JSON array of option objects with the following fields:
  * id: the unique identifier of the option
  * name: the name of the option
  * option_type: the type of the option, either "call" or "put"
  * strike: the strike price of the option
  * time_to_maturity: the time to maturity of the option
  * risk_free_rate: the risk-free rate used to calculate the option price
  * volatility: the volatility used to calculate the option price
  * future_price: the future price used to calculate the option price
  * black76_price: the Black 76 price of the option (if calculated) 

##Testing 
To run the tests, run python -m pytest in the project directory.
