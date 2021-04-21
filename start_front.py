import uvicorn
from services.http_front.app.core import app

if __name__ == "__main__":
    uvicorn.run(app)