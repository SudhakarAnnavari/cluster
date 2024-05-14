from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import inspect
from sqlalchemy.sql import text
import uuid

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure PostgreSQL SQLAlchemy connection URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://airlinedb_user:AVNS_SFBbzpFCBpvhgbI5M1T@postgres-v1-dbs-do-user-13186796-0.b.db.ondigitalocean.com:25060/gstservice_db'  # Replace with your PostgreSQL URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://airlinedb_user:AVNS_SFBbzpFCBpvhgbI5M1T@ec2-65-1-12-129.ap-south-1.compute.amazonaws.com:5432/gstservice_db'  # Replace with your PostgreSQL URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)
# Generate model dynamically
Base = automap_base()

# Generate model dynamically
with app.app_context():

    Base.prepare(db.engine, reflect=True)
    Base.query = db.session.query_property()  # Manually initialize query property on Base


# Use the generated model
MyTable = Base.classes.users

@app.route('/api/users', methods=['GET'])
@cross_origin()  # Enable CORS on this route
def fetch_users():
    items = MyTable.query.all()  # Fetch all rows from the 'users' table
    result = []
    for item in items:
        row_data = {col: getattr(item, col) for col in item.__table__.columns.keys()}
        result.append(row_data)
    return jsonify(result)  # Returns data as JSON


@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    # Fetch the user by ID
    user = MyTable.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update the cluster_id from the request JSON
    new_cluster_id = request.json.get('cluster_id')
    if new_cluster_id:
        user.cluster_id = new_cluster_id
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'error': 'No cluster ID provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)