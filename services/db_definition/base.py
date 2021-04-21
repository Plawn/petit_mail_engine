from typing import Optional
from pony.orm import Database, db_session
from dataclasses import dataclass

database = Database()


@dataclass
class DBSettings:
    username: str
    password: str
    host: str
    port: str
    database: str


def init_db(settings: DBSettings, drop_database: bool = False):
    # recreate_db = settings['recreate_db']
    database.bind(
        provider='postgres',
        user=settings.username,
        password=settings.password,
        host=settings.host,
        database=settings.database
    )

    if drop_database:
        database.generate_mapping(check_tables=False)
        database.drop_all_tables(with_all_data=True)
        database.create_tables()
        # note: not clean
        from .identity import Identity
        from .sender import Sender
        with db_session:
            i = Identity(name="kiwi")
            s = Sender(
                credentials={}, 
                quota=400, 
                email="kiwi-auth@cnje.org",
                identity=i
            )
    else:
        try:
            database.generate_mapping(create_tables=True)
        except:
            pass


credentials = DBSettings(
    'root', 'root', 'localhost', '5432', 'mail_engine'
)
