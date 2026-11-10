from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    # Verifica se o utilizador 'admin' já existe usando a nova classe User
    if not User.get_by_username("admin"):
        admin = User(username="admin")
        admin.set_password("123456")
        admin.save()
        print("Utilizador 'admin' criado com sucesso com a classe User!")
    else:
        print("O utilizador 'admin' já existe no banco de dados.")