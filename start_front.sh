# we have to be top level in order to be able to use the common imports for the db
uvicorn services.http_front.app.core:app --reload --port 5000