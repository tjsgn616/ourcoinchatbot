from app.sc import app
from app.weather import app
if __name__ == "__main__":
    app.run(threaded=True, port=5000)