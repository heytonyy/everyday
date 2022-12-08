from flask_app import app
from flask_app.controllers import login_controller, day_controller, friend_controller, account_controller

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)