import os
from flask import Flask, redirect, url_for

def create_app():
    # Caminho absoluto garantido para a pasta app/templates
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    
    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = 'chave_secreta_biblioteca'

    # Regista o blueprint de autenticação
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Rota raiz: redireciona para a página da biblioteca
    @app.route('/')
    def index():
        return redirect(url_for('auth.welcome'))

    return app