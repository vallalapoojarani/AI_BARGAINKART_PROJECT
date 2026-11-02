import os
from flask import Flask, render_template
from config import Config
from models import db, login_manager
from routes import register_blueprints

def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register all Blueprints
    register_blueprints(app)

    # Template context processors
    @app.context_processor
    def inject_global_data():
        from flask_login import current_user
        from models.models import CartItem, Wishlist

        cart_count = 0
        wishlist_count = 0
        if current_user.is_authenticated:
            try:
                cart_count = sum(item.quantity for item in CartItem.query.filter_by(user_id=current_user.id).all())
                wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()
            except Exception:
                cart_count = 0
                wishlist_count = 0

        def format_inr(val):
            try:
                val = float(val)
                return f"₹{val:,.0f}"
            except Exception:
                return f"₹{val}"

        return dict(
            cart_count=cart_count,
            wishlist_count=wishlist_count,
            format_inr=format_inr
        )

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

# WSGI Application
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        # Auto-seed if database is new
        from models.models import User
        if not User.query.filter_by(email='demo@bargainkart.com').first():
            print("Auto-seeding demo database...")
            from database.seed import seed_database
            seed_database()

    port = int(os.environ.get('PORT', 5000))
    debug = bool(os.environ.get('FLASK_DEBUG', True))
    print(f"Starting BARGAINKART on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
