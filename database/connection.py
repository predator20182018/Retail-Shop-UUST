from sqlmodel import SQLModel, Session, create_engine

database_file = "retail_shop.db"
database_connection_string = f"sqlite:///{database_file}"

connect_args = {"check_same_thread": False}
engine = create_engine(
    database_connection_string,
    echo=False,
    connect_args=connect_args
)


def init_db():
    # Импортируем модели таблиц, чтобы SQLModel создал их в файле БД
    from models.products import Product
    from models.orders import Order
    from models.users import CustomerInDB
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session