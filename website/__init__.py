from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .admin_view import AdminModelView, ProductAdmin
import os



db = SQLAlchemy()
DB_NAME = 'musicshop.sqlite3'


def create_database():
    db.create_all()
    print('Database Created')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'wie5ugvsehorawpefioauoncw'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = 'media'
    

    db.init_app(app)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))
    
    

    from .views import views
    from .auth import auth
    # from .admin import like_admin
    from .models import Customer, Cart, Product, Order

    app.register_blueprint(views, url_prefix='/') # localhost:5000/about-us
    app.register_blueprint(auth, url_prefix='/') # localhost:5000/auth/change-password
    # app.register_blueprint(like_admin, url_prefix='/')
    
    
    
    admin_panel = Admin(app, name='Admin Panel', template_mode='bootstrap4')

    # Реєстрація моделей у Flask-Admin
    admin_panel.add_view(AdminModelView(Customer, db.session))
    admin_panel.add_view(AdminModelView(Cart, db.session))
    admin_panel.add_view(ProductAdmin(Product, db.session))
    admin_panel.add_view(AdminModelView(Order, db.session))


    with app.app_context():
        create_database()

    return app

