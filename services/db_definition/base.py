import os
from dataclasses import dataclass
import yaml
from pony.orm import Database, db_session

database = Database()


@dataclass
class DBSettings:
    """Contains the differents fields in order to connect the worker and the http front to the database
    """
    username: str
    password: str
    host: str
    port: str
    database: str


def init_db(settings: DBSettings, drop_database: bool = False):
    """
    Will init the database object in order to be used
    """
    print(settings)
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


def load_settings():
    with open(os.environ.get('CONF_FILE', 'conf.yaml'), 'r') as f:
        conf = yaml.safe_load(f)['database']
        return DBSettings(
            conf['username'], conf['password'], conf['host'], conf['port'], conf['database'],
        )


credentials = load_settings()
