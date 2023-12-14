from src.api import app
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host= "127.0.0.1", port=8088, reload=True, log_level="info")