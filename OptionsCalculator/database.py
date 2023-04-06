from sqlmodel import Field, SQLModel, create_engine, Session, select

file_name = "options.db"
sqlite_url = f"sqlite:///{file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True,
                       connect_args=connect_args)  # make the engine print everything it does in SQL for debugging


def create_tables_and_db():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


def get_session():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise
