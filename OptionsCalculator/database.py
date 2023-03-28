from sqlmodel import Field, SQLModel, create_engine, Session, select


file_name = "options.db"
sqlite_url = f"sqlite:///{file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)  # make the engine print everything it does in SQL for debugging


def create_tables_and_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


