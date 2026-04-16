import os
import logging
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, flash, redirect, request, render_template
from config import Config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.support import support_bp
    from routes.admin import admin_bp
    from routes.super_admin import super_admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(super_admin_bp)

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        flash('An unexpected error occurred. Please try again.', 'danger')
        return render_template('errors/500.html'), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        flash('An unexpected error occurred. Please try again.', 'danger')
        referrer = request.referrer
        if referrer:
            return redirect(referrer)
        return render_template('errors/500.html'), 500

    logger.info("GyanPustak application started successfully!")
    return app

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app = create_app()
    app.run(debug=debug, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
