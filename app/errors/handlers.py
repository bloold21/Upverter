from flask import render_template
from app.errors import bp as erros_bp

@erros_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('erros/404.html'), 404


@erros_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500