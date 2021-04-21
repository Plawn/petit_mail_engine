import os
import sys

from services.worker.app.worker import start_worker

if __name__ == '__main__':
    conf_filename = 'conf.yaml'
    template_provider = 'local'
    try:
        start_worker(conf_filename, template_provider)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
