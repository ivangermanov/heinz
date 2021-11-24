# region Set up of Flask
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
import os
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from pickle import load
import config
from bench import FeatureInstance as FI


# Init app

app = Flask(__name__)

# endregion

# region Set up of Database

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)
# endregion

# region Set up of database models


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(400))

    def __init__(self, title, description):
        # Add the data to the instance
        self.title = title
        self.description = description


class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')


todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)
# endregion

# region Set up of routes

CORS(app, resources={r"/api": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
# endregion

# region Set up API


@app.route('/api/todo', methods=['POST'])
@cross_origin(origin='*', headers=['content-type'])
def add_todo():
    # get the data
    title = request.json['title']
    description = request.json['description']

    # Create an instance
    new_todo = Todo(title, description)

    # Save the todo in the db
    db.session.add(new_todo)
    db.session.commit()

# return the created todo
    return todo_schema.jsonify(new_todo)

# Get all todos


@app.route('/api/todo', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_todos():
    # get the todos from db
    all_todos = Todo.query.all()
    # get the todos as per the schema
    result = todos_schema.dump(all_todos)
    # return the todos
    return jsonify(result)

# Get a single todo

@app.route('/api/todo/<id>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def get_prediction(line_tag):
    model = load(open(os.path.join(config.MODELS_PATH,
                                   config.MODEL_NAMES[line_tag]),
                                   "rb"))

    # TODO: Refactor for dummy_deploy functionality
    feature_instance = FI(training = True,
                          granular=False,
                          on=config.AI_id,
                          line = line_tag,
                          estimator_params=config.estimator_params,
                          dummy_deploy=False)

    testing_data = feature_instance.fetch()["XYdates_test"]
    dates = testing_data[2]
    current_date_idx = list(dates).index(config.CURRENT_DATE)
    dates = dates[:current_date_idx + 2]
    Y_true = testing_data[0][:current_date_idx + 1]

    X_test = testing_data[1].iloc[:current_date_idx + 1, :]
    Y_pred = model.predict(X_test)

    X_next = X_test.iloc[current_date_idx + 1, :]
    Y_pred_next = model.predict(X_next)
    date_next = dates[-1]
    
    return_object = {
        "True labels": Y_true,
        "Predicted labels": Y_pred,
        "Dates": dates[:-1],
        "Next prediction": Y_pred_next,
        "Next date": date_next
    }
    return jsonify(return_object)


@app.route('/api/todo/<id>', methods=['PUT'])
@cross_origin(origin='*', headers=['Content-Type'])
def update_todo(id):
    # get the todo first
    todo = Todo.query.get(id)
    # get the data
    title = request.json['title']
    description = request.json['description']

    # set the data
    todo.title = title
    todo.description = description

    # commit to the database
    db.session.commit()

    # return the new todo as per the schema
    return todo_schema.jsonify(todo)

# Delete a todo


@app.route('/api/todo/<id>', methods=['DELETE'])
@cross_origin(origin='*', headers=['Content-Type'])
def delete_todo(id):
    # get the todo to be deleted
    todo = Todo.query.get(id)

    # delete from the database
    db.session.delete(todo)

    # commit on the database
    db.session.commit()

    # return thr deleted todo as per the schema
    return todo_schema.jsonify(todo)


# endregion

# region Start the app
if __name__ == '__main__':
    app.run(debug=True)
# endregion