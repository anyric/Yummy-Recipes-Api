""" module to manage category"""
from datetime import datetime
from apps import db, ma
from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_marshmallow import Marshmallow


class Category(db.Model):
    """model to store recipe categroy"""
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    date_modified = db.Column(db.DateTime, nullable=False)



    def __init__(self, user_id, name, description):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.date_modified = datetime.utcnow()

    def save(self):
        """method to store new category"""
        db.session.add(self)
        db.session.commit()

    def update(self, category_name, description):
        """method to update category"""
        self.name = category_name
        self.description = description
        self.date_modified = datetime.utcnow()
        self.save()

    def delete(self):
        """method to delete a category"""
        db.session.delete(self)
        db.session.commit()
    @staticmethod
    def get_category_by_id(category_id, current_user):
        """method to get a category by id"""
        category = Category.query.filter(Category.id == category_id, \
                                        Category.user_id == current_user.id).first()
        return category

    @staticmethod
    def get_category_by_name(category_name, current_user):
        """method to get a category by id"""
        category = Category.query.filter(Category.name.ilike("%" + category_name + "%"), \
                                        Category.user_id == current_user.id).first()
        return category

class CategorySchema(ma.Schema):
    """class to create category model for pagination"""
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(1))
    description = fields.String(required=True, validate=validate.Length(1))
    user_id = fields.Integer()
    date_modified = fields.DateTime()
    url = ma.URLFor('view_category', id='<id>', _external=True)

    @pre_load
    def process_category(self, data):
        """method to process the category data"""
        category = data.get('category')
        if category:
            if isinstance(category, dict):
                category_name = category.get('name')
            else:
                category_name = category
            category_dict = dict(name=category_name)
        else:
            category_dict = {}
        data['category'] = category_dict
        return {data}
