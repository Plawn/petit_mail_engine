import logging
from services.worker.app.senders.gmail_implem import GmailEmailSender
from typing import Dict, Type

import yaml

from .data_structure import Context
from .senders import EmailSender
from .senders import engines as mail_engines
from .senders.sender_identity import Identity
from .template_db import engines as template_db_engines
from .template_db.interface import TemplateDB


def load_mail_senders(creds: dict) -> Dict[str, EmailSender]:
    senders_db: Dict[str, EmailSender] = {
        # fix me

    }
    for name, infos in creds.items():
        type_ = infos['type']
        del infos['type']
        if type_ == "gmail":
            senders_db[name] = GmailEmailSender.of(infos)
    return senders_db


def get_template_provider(template_infos: dict, type_: str) -> TemplateDB:
    try:
        engine = template_db_engines[type_]
        return engine(engine.get_creds_form()(**template_infos[type_]))
    except KeyError as e:
        raise KeyError(
            f'Invalid template engine selected, availables are {list(template_db_engines.keys())}, got {type_}'
        )
    except Exception as e:
        raise e


def load_context(creds_filename: str, template_provider: str) -> Context:
    """Will load and prepare the context for the app
    """
    with open(creds_filename, 'r') as f:
        conf = yaml.safe_load(f)

    context = Context()

    context.senders_db = load_mail_senders(conf['creds'])
    context.template_db = get_template_provider(
        conf['templates'], template_provider
    )

    return context


def make_template_filename(template_name: str):
    return template_name + '.html'
