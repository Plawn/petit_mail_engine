import os
from dataclasses import dataclass
import yaml
from pony.orm import Database, db_session
from typing import Optional

database = Database()

bound_db = False

@dataclass
class DBSettings:
    """Contains the differents fields in order to connect the worker and the http front to the database
    """
    username: str
    password: str
    host: str
    port: str
    database: str

@dataclass
class MinimalSettings:
    name: str
    email: str
    quota: int
    credentials: dict


def init_db(settings: DBSettings, minimalSettings: Optional[MinimalSettings] = None, drop_database: bool = False):
    """
    Will init the database object in order to be used
    """
    global bound_db
    if bound_db:
        return
    database.bind(
        provider='postgres',
        user=settings.username,
        password=settings.password,
        host=settings.host,
        database=settings.database,
        port=settings.port,
    )
    bound_db = True

    if drop_database:
        database.generate_mapping(check_tables=False)
        database.drop_all_tables(with_all_data=True)
        database.create_tables()
    else:
        try:
            database.generate_mapping(create_tables=True)
        except:
            pass
    if minimalSettings is not None:
                # note: not clean
        from .identity import Identity
        from .sender import Sender
        with db_session:
            current_identity = Identity.get(name=minimalSettings.name)
            if current_identity is None:
                current_identity = Identity(name=minimalSettings.name)
            current_sender = Sender.get(email=minimalSettings.email)
            if current_sender is None:
                s = Sender(
                    credentials=minimalSettings.credentials,
                    quota=minimalSettings.quota,
                    email=minimalSettings.email,
                    identity=current_identity
                )



def load_settings() -> Tuple[DBSettings, Optional[MinimalSettings]]:
    with open(os.environ.get('CONF_FILE', 'conf.yaml'), 'r') as f:
        conf = yaml.safe_load(f)
        d = conf['database']
        db_settings = DBSettings(
            d['username'], d['password'], d['host'], d['port'], d['database'],
        )
        if "minimal_settings" in d:
            m = d["minimal_settings"]
            minimal_settings = MinimalSettings(m["name"], m["email"], m["quota"], m["credentials"])
            return db_settings, minimal_settings
        return db_settings, None


(credentials, minimal_settings) = load_settings()
