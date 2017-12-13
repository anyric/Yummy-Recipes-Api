""" module to manage category"""
from apps import db

class Category(db.Model):
    """model to store recipe categroy"""
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    date_modified = db.Column(db.DateTime, nullable=False)


    def __init__(self, user_id, name, description, date_modified):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.date_modified = date_modified

    def save(self):
        """method to store new category"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getcategory(user_id):
        """method to retrieve category"""
        categories = Category.query.filter_by(user_id=user_id)
        results = []
        if categories is not None:
            for categorylist in categories:
                obj = {
                    'id': categorylist.id,
                    'name': categorylist.name,
                    'user': categorylist.user_id,
                    'description': categorylist.description,
                    'date_modified':categorylist.date_modified
                    }
                results.append(obj)
                return results

        return {"message":"No category found"}

    def delete(self):
        """method to delete a category"""
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        return 'name {}'.format(self.name)
