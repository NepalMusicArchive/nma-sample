from flask import Flask
from nml import app
# from waitress import serve

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
    # serve(app, host='0.0.0.0', port=8000)
