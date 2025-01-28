from flask import Flask

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder='../html/template', static_folder='../html/static')
        self.register_routes()

    def register_routes(self):
        from routes import register_blueprints
        register_blueprints(self.app)

    def run(self):
        self.app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    flask_app = FlaskApp()
    flask_app.run()
