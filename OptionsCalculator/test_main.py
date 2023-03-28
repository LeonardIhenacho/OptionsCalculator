import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


from .app import app, get_session, Option


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


def test_black76_price(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=42, maturity=1.5, risk_free_rate=0.05, volatility=0.2,
                      future_price=42, option_type='call')
    session.add(option_1)
    session.commit()

    response = client.patch(f'options_black76/{option_1.id}')
    data = response.json()

    assert round(data['black76_price'], 3) == 3.798



def test_create_option(client: TestClient):
    response = client.post("/options/",
                           json={'name': 'Leo_test_option1', 'strike': 10, 'maturity': 1.5, 'risk_free_rate': 1.5,
                                 'volatility': 2,
                                 'future_price': 10, 'option_type': 'call'})

    data = response.json()

    assert response.status_code == 200
    assert data['name'] == 'Leo_test_option1'
    assert data['strike'] == 10
    assert data['maturity'] == 1.5
    assert data['risk_free_rate'] == 1.5
    assert data['volatility'] == 2
    assert data['future_price'] == 10
    assert data['id'] is not None
    assert  data['option_type'] == 'call'


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


def test_read_options(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=12, maturity=1.5, risk_free_rate=1.5, volatility=2,
                      future_price=10, option_type='call')
    option_2 = Option(name='Leo_test_option2', strike=11, maturity=1, risk_free_rate=1, volatility=2,
                      future_price=10, option_type='put')
    session.add(option_1)
    session.add(option_2)
    session.commit()

    response = client.get('/options/')
    data = response.json()

    assert response.status_code == 200
    assert data[0]['name'] == option_1.name
    assert data[0]['strike'] == option_1.strike
    assert data[0]['maturity'] == option_1.maturity
    assert data[0]['risk_free_rate'] == option_1.risk_free_rate
    assert data[0]['volatility'] == option_1.volatility
    assert data[0]['future_price'] == option_1.future_price
    assert data[0]['option_type'] == option_1.option_type
    assert data[1]['name'] == option_2.name
    assert data[1]['strike'] == option_2.strike
    assert data[1]['maturity'] == option_2.maturity
    assert data[1]['risk_free_rate'] == option_2.risk_free_rate
    assert data[1]['volatility'] == option_2.volatility
    assert data[1]['future_price'] == option_2.future_price
    assert data[1]['option_type'] == option_2.option_type


def test_read_option(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=12, maturity=1.5, risk_free_rate=1.5, volatility=2,
                      future_price=10, option_type='call')

    session.add(option_1)
    session.commit()

    response = client.get(f'/options/{option_1.id}')
    data = response.json()

    assert response.status_code == 200
    assert data['name'] == option_1.name
    assert data['strike'] == option_1.strike
    assert data['maturity'] == option_1.maturity
    assert data['risk_free_rate'] == option_1.risk_free_rate
    assert data['volatility'] == option_1.volatility
    assert data['future_price'] == option_1.future_price
    assert data['id'] == option_1.id
    assert data['option_type'] == option_1.option_type


def test_delete_option(session: Session, client: TestClient):
    option_1 = Option(name='Leo_test_option1', strike=12, maturity=1.5, risk_free_rate=1.5, volatility=2,
                      future_price=10, option_type='call')
    session.add(option_1)
    session.commit()

    response = client.delete(f"/options/{option_1.id}")
    option_db = session.get(Option, option_1.id)

    assert option_db is None
    assert response.status_code == 200
