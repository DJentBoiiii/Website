
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_login import current_user
from flask import redirect, url_for
from flask_wtf.file import FileField
from flask_admin.helpers import get_url
from werkzeug.utils import secure_filename
import os



class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    
    
    
    
class ProductAdmin(ModelView):
    form_extra_fields = {
        'product_picture': FileField(
            'Product Picture'
        )
    }

    def on_model_change(self, form, model, is_created):
        if form.product_picture.data:

            file = form.product_picture.data
            
            filename = secure_filename(file.filename)
            
            upload_folder = './website/static/images/products'
            upload_path = os.path.join(upload_folder, filename)
            
            os.makedirs(upload_folder, exist_ok=True)
            
            file.save(upload_path)

            model.product_picture = f'../static/images/products/{filename}'

        return super(ProductAdmin, self).on_model_change(form, model, is_created)