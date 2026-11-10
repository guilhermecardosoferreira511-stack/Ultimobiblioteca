from flask import redirect, request, session, url_for


def init_app_middlewares(app):
    """Registra os middlewares da aplicação."""

    @app.before_request
    def check_auth():
        # Defina as rotas/endpoints que são públicos (não exigem login)
        rotas_livres = [
            "main.index",
            "auth.login",
            "static",
        ]

        # Se a rota atual não for livre e o usuário não estiver logado
        if (
            request.endpoint
            and request.endpoint not in rotas_livres
            and not request.endpoint.startswith("static")
        ):
            if "usuario_logado" not in session:
                return redirect(url_for("auth.login"))