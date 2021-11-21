from flask import Flask

## Init app

app = Flask(__name__)

# Start the app
if __name__ == '__main__':
    app.run(debug=True)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(400))

    def __init__(self,title,description):
        # Add the data to the instance
        self.title = title
        self.description = description

class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id','title','description')

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)