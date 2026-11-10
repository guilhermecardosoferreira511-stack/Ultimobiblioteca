from flask import Blueprint, redirect, session, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if "usuario_logado" in session:
        return redirect(url_for("auth.welcome"))
    return redirect(url_for("auth.login"))