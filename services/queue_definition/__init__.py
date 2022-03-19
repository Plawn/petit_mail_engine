import os

import yaml
from kafka import KafkaConsumer, KafkaProducer

QUEUE_NAME = 'mail_queue'

def get_consumer() -> KafkaConsumer:
    # TODO: make pretty
    conf = get_conf()
    
    rabbitHost = conf['host']
    rabbit_user = conf['user']
    rabbit_password = conf['password']
    
    consumer = KafkaConsumer('my_favorite_topic')
    
    return consumer

def get_conf():
    # TODO: not optimal but good enough
    with open(os.environ.get('CONF_FILE', "conf.yaml"), 'r') as f :
        conf = yaml.safe_load(f)['queue']
    return conf

def get_producer() -> KafkaProducer: 
    # TODO: make pretty
    conf = get_conf()
    producer = KafkaProducer('my_favorite_topic')
    
    
    return producer
