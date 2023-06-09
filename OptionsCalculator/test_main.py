import pytest
from math import isclose
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from .PVCalculationEngine import OptionsCalculator

from .app import app, get_session, Option, OptionUpdate, OptionCreate, OptionRead


# Use pytest fixture so that this code is run before all tests are executed and can be used by all tests.
@pytest.fixture(name='session')
def session_fixture():
    # Create an im memory testing db that is never written to any file and is deleted after use.
    engine = create_engine("sqlite://",
                           connect_args={"check_same_thread": False},
                           poolclass=StaticPool)

    SQLModel.metadata.create_all(engine)
    # This works because we import from the main 'app'. The tables are therefore saved in metadata - we call them.
    with Session(engine) as session:
        yield session


@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session

    # Override the main session dependency so that we can use a separate test database
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client

    # remove the override after we have used it for the test.
    app.dependency_overrides.clear()


def test_call_option_price():
    assert isclose(OptionsCalculator.calculate_price(42, 1.5, 0.05, 0.2, 42, 'call'), 3.782, rel_tol=0.01)


def test_put_option_price():
    assert isclose(OptionsCalculator.calculate_price(42, 1.5, 0.05, 0.2, 42, 'put'), 3.782, rel_tol=0.01)


def test_wrong_option_type():
    with pytest.raises(ValueError):
        OptionsCalculator.calculate_price(42, 1.5, 0.05, 0.2, 42, 'wrong_option_type')


def test_negative_strike():
    with pytest.raises(ValueError):
        OptionsCalculator.calculate_price(-42, 1.5, 0.05, 0.2, 42, 'call')


def test_negative_time_to_maturity():
    with pytest.raises(ValueError):
        OptionsCalculator.calculate_price(42, -1.5, 0.05, 0.2, 42, 'call')


def test_None_time_to_maturity():
    with pytest.raises(TypeError):
        OptionsCalculator.calculate_price(42, None, 0.05, 0.2, 42, 'call')


def test_missing_sigma():
    with pytest.raises(TypeError):
        OptionsCalculator.calculate_price(42, 1.5, 0.05, 42, 'call')


# Test creating an option.
def test_create_option(session: Session, client: TestClient):
    response = client.post("/options/",
                           json={'name': 'Leo_test_option1',
                                 'strike': 10,
                                 'time_to_maturity': 1.5,
                                 'risk_free_rate': 1.5,
                                 'volatility': 2,
                                 'future_price': 10,
                                 'option_type': 'call'})

    data = response.json()

    assert response.status_code == 200
    assert data['name'] == 'Leo_test_option1'
    assert data['strike'] == 10
    assert data['time_to_maturity'] == 1.5
    assert data['risk_free_rate'] == 1.5
    assert data['volatility'] == 2
    assert data['future_price'] == 10
    assert data['id'] is not None
    assert data['option_type'] == 'call'


# Test reading one option
def test_read_option(session: Session, client: TestClient):
    response = client.post("/options/",
                           json={'name': 'Leo_test_option1',
                                 'strike': 10,
                                 'time_to_maturity': 1.5,
                                 'risk_free_rate': 1.5,
                                 'volatility': 2,
                                 'future_price': 10,
                                 'option_type': 'call'})

    assert response.status_code == 200
    option_id = response.json()["id"]
    read_response = client.get(f"/options/{option_id}")
    print(read_response.json())
    assert read_response.status_code == 200
    data = read_response.json()
    assert "id" in data
    assert data["name"] == 'Leo_test_option1'
    assert data["strike"] == 10
    assert data["option_type"] == 'call'
    assert data["time_to_maturity"] == 1.5
    assert data["risk_free_rate"] == 1.5
    assert data["volatility"] == 2
    assert data["future_price"] == 10


# Test creating an option, then updating it with the Black76 price.
def test_black76_price(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=42, time_to_maturity=1.5, risk_free_rate=0.05, volatility=0.2,
                      future_price=42, option_type='call')
    session.add(option_1)
    session.commit()

    response = client.patch(f'options_black76/{option_1.id}')
    data = response.json()

    assert round(data['black76_price'], 3) == 3.798


def test_read_options(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=12, time_to_maturity=1.5, risk_free_rate=1.5, volatility=2,
                      future_price=10, option_type='call')
    option_2 = Option(name='Leo_test_option2', strike=11, time_to_maturity=1, risk_free_rate=1, volatility=2,
                      future_price=10, option_type='put')
    session.add(option_1)
    session.add(option_2)
    session.commit()

    response = client.get('/options/')
    data = response.json()

    assert response.status_code == 200
    assert data[0]['name'] == option_1.name
    assert data[0]['strike'] == option_1.strike
    assert data[0]['time_to_maturity'] == option_1.time_to_maturity
    assert data[0]['risk_free_rate'] == option_1.risk_free_rate
    assert data[0]['volatility'] == option_1.volatility
    assert data[0]['future_price'] == option_1.future_price
    assert data[0]['option_type'] == option_1.option_type
    assert data[1]['name'] == option_2.name
    assert data[1]['strike'] == option_2.strike
    assert data[1]['time_to_maturity'] == option_2.time_to_maturity
    assert data[1]['risk_free_rate'] == option_2.risk_free_rate
    assert data[1]['volatility'] == option_2.volatility
    assert data[1]['future_price'] == option_2.future_price
    assert data[1]['option_type'] == option_2.option_type


def test_update_option(client: TestClient, session: Session):
    response = client.post("/options/",
                           json={'name': 'Leo_test_option1',
                                 'strike': 10,
                                 'time_to_maturity': 1.5,
                                 'risk_free_rate': 1.5,
                                 'volatility': 2,
                                 'future_price': 10,
                                 'option_type': 'call'})

    data = response.json()

    update_data = {"name": "Updated Option Name"}
    response2 = client.patch(f"/options/{data['id']}", json=update_data)
    updated_option = response2.json()
    assert response2.status_code == 200
    assert updated_option["name"] == update_data["name"]
    assert updated_option["strike"] == data['strike']
    assert updated_option["option_type"] == data['option_type']
    assert updated_option["time_to_maturity"] == data['time_to_maturity']
    assert updated_option["risk_free_rate"] == data['risk_free_rate']
    assert updated_option["volatility"] == data['volatility']
    assert updated_option["future_price"] == data['future_price']



def test_delete_option(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=12, time_to_maturity=1.5, risk_free_rate=1.5, volatility=2,
                      future_price=10, option_type='call')
    session.add(option_1)
    session.commit()

    response = client.delete(f"/options/{option_1.id}")
    option_db = session.get(Option, option_1.id)

    assert option_db is None
    assert response.status_code == 200


def test_delete_nonexistent_option(session: Session, client: TestClient):

    response = client.delete(f"/options/1000")

    assert response.status_code == 500  # Not found



def test_incomplete_option(client: TestClient):
    # No strike price
    response = client.post("/options/",
                           json={'name': 'Leo_test_option1', 'maturity': 1.5, 'risk_free_rate': 1.5,
                                 'volatility': 2,
                                 'future_price': 10})

    assert response.status_code == 422


def test_invalid_option(client: TestClient):
    # Volatility is an invalid type
    response = client.post("/options/",
                           json={'name': 'Leo_test_option1', 'strike': 10, 'maturity': 1.5, 'risk_free_rate': 1.5,
                                 'volatility': 'really volatile',
                                 'future_price': 10, 'options_type': 'call'})

    assert response.status_code == 422





