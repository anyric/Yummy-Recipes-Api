""" module to manage category"""
from apps import db

class Category(db.Model):
    """model to store recipe categroy"""
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))

    def __init__(self, user_id, name, description):
        self.user_id = user_id
        self.name = name
        self.description = description

    def save(self):
        """method to store new category"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getcategory(user_id):
        """method to retrieve category"""
        categories = Category.query.filter_by(user_id=user_id)
        results = []
        
        for categorylist in categories:
            obj = {
                    'id': categorylist.id,
                    'name': categorylist.name,
                    'user': categorylist.user_id,
                    'description': categorylist.description
                }
            results.append(obj)
            #response = jsonify(results)

        return results#response
        

    def delete(self):
        """method to delete a category"""
        db.session.delete(self)
        db.session.commit()



    def __repr__(self):
        return 'name {}'.format(self.name)



"""
class Category():
   #class to manipulate category
   def createcategory(self, user_id, name, description):
        #insert category into the category table
        category = Category(user_id, name, description)
        db.session.add(category)
        db.session.commit()

    def viewcategory(self, user_id):
        #unction to view user recipe category
        categories = models.Category.query.filter_by(user_id=user_id)
        results = []
        for category in categories:
            result = dict(category_name=category.name, category_id=category.id, category_description=category.description, user=user_id)
            results.append(result)
        return results


    def getcategory(self, name):
        #function to get recipe category
        category = models.Category.query.filter_by(name=name).first_or_404()
        return category


    def updatecategory(self, category, name, decription):
        #function to uodate category details
        category_item = models.Category.query.get(category.id)
        category_item.name = name
        category_item.description = decription
        db.session.commit()


    def deletecategory(self, name):
        #function to delete a category in database
        category = models.Category.query.filter_by(name=name).first()
        db.session.delete(category)
        db.session.commit()
"""