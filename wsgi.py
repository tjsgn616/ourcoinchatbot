from app.sc import app
from app.weather import app2
if __name__ == "__main__":
    app.run(threaded=True, port=5000)
    app2.run(threaded=True, port=5000)