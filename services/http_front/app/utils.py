

import json
from typing import List, Tuple
import logging
import traceback
from ...db_definition import (Content, Email, Identity, Recipient, Sender,
                              database)
from ...queue_definition import QUEUE_NAME, get_channel, configurer

channel = get_channel(configurer, False)

def get_one_recipient(email: str):
  try:
    return Recipient.get(email=email) or Recipient(email=email)
  except Exception as e:
    print(e)
    return None

def get_recipients_stage_one(email_list: List[str]):
  res = []
  for email in email_list:
    r = get_one_recipient(email)
    if r is not None:
      res.append(r)
  return res
 
def get_recipients_from_emails(emails: List[List[str]]) -> List[Recipient]:
    # TODO:
    # documentation
    # check if exists in db
    # create recipient entity for each not existing
    # TODO: optimize
    res = [
        get_recipients_stage_one(email_list) for email_list in emails
    ]
    return res


def push_mails_to_queue(emails: List[Email]) -> None:
    # TODO:
    # documentation
    # TODO: not pretty
    global channel
    retries = 0
    to_send = [*emails]
    while len(to_send) > 0 and retries < 5:
        email = to_send.pop()
        try:
            channel.publish(json.dumps({'id': email.id}))
        except Exception as e:
            channel = get_channel(configurer, False).open()
            logging.error(traceback.format_exc())
            to_send.append(email)
    

def get_identities_for_emails(identity: Identity, addresses: List[List[str]]) -> List[Sender]:
    # TODO:
    # documentation
    number = 0
    for a in addresses:
        number += len(a)
    identity_id = identity.id
    # TODO: use plain pony orm ?
    available_senders: List[Tuple[int, int]] = list(database.select(
        """select
                i.id,
                i.remaning
            from
                (
                    SELECT
                        s.*,
                        s.quota - s.pending - (
                            select
                                count(r.*)
                            from
                                email e
                                join sender s on s.id = e.sender
                                join email_recipient er on er.email = e.id
                                join recipient r on er.recipient = r.id
                            where
                                age(e.sent_at) < '24h'
                        ) as remaning
                    FROM
                        sender s
                        JOIN identity i on i.id = s.identity
                    where
                        i.id = $identity_id
                    group by
                        s.id
                ) as i
            where
                remaning > 0;
    """))
    # todo: clean
    # todo: handle case where not enough quota is available now
    remaining = number
    res = []
    for sender_id, available in available_senders:
        sender = Sender[sender_id]
        if remaining <= available:
            res.extend([sender for _ in range(remaining)])
            sender.pending += remaining
        else:
            res.extend([sender for _ in range(available)])
            sender.pending += available
    return res


def send_mail(identity: str, content: List[Content], from_: str, adresses: List[List[str]]) -> Content:
    # TODO:
    # documentation
    ident = Identity.get(name=identity)
    recipients = get_recipients_from_emails(adresses)
    senders = get_identities_for_emails(ident, adresses)
    emails = [
        Email(
            identity=ident,
            from_=from_,
            content=c,
            recipient=recipient,
            sender=sender,
        ) for recipient, sender, c in zip(recipients, senders, content)  # clean content
    ]
    database.commit()
    # save
    # push ids to queue
    push_mails_to_queue(emails)
