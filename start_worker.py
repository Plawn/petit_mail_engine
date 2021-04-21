from services.worker.app.worker import main
import sys
import os

if __name__ == '__main__':
    try:
        main('conf.yaml')
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
