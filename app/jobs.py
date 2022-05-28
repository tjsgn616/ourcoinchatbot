from flask import Flask
app = Flask(__name__)
@app.route('/price', methods=['POST'])
def func_9():
    test = {
                    "version": "2.0",
                    "template": {
                    "outputs": [
                    {
                    "simpleText": {
                    "text":  "test ese"
                }
            }
        ]
    }
        }       
    return (test)