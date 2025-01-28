from flask import Flask, redirect, url_for

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder='../html/templates', static_folder='../html/static')
        self.register_routes()

    def register_routes(self):
        from routes import register_blueprints
        register_blueprints(self.app)

        @self.app.route('/')
        def home():
            return redirect(url_for('main_routes.status'))

    def run(self):
        self.app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    flask_app = FlaskApp()
    flask_app.run()
