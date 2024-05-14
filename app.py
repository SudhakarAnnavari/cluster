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
MyTable = Base.classes.clusters
UserTable = Base.classes.users



@app.route('/api/clusters', methods=['GET'])
@cross_origin()  # Enable CORS on this route
def fetch_gst_creds():

    items = MyTable.query.all()  # Fetch all rows from the table 
    result = []
    for item in items:
        row_data = {col: getattr(item, col) for col in item.__table__.columns.keys()}  
        print(row_data)
        result.append(row_data)
    return jsonify(result)  # Returns data as JSON



@app.route('/api/clusters/<id>', methods=['GET'])
@cross_origin()  # Enable CORS on this route
def fetch_single_cluster(id):
    cluster = MyTable.query.get(id)  # Fetch the cluster with the given ID
    if cluster is None:
        return jsonify({'error': 'Cluster not found'}), 404  # Return a 404 error if cluster is not found
    
    # Construct JSON response for the single cluster
    cluster_data = {col: getattr(cluster, col) for col in cluster.__table__.columns.keys()}  
    return jsonify(cluster_data)  # Return data for single cluster as JSON

    
# Route to add new data
@app.route('/api/clusters', methods=["POST"])
@cross_origin()  # Enable CORS on this route
def add_cluster():
    data = request.get_json()

    # Extract data from the request
    name = data.get('name')
    workspaces = data.get('workspaces')  # Corrected to match frontend data key

    # Create a new row object
    new_row = MyTable(id=uuid.uuid4(), name=name, workspaces=workspaces)
    try:
        # Add the new row to the session and commit the transaction
        db.session.add(new_row)
        db.session.commit()
        return jsonify({'message': 'Data added successfully'}), 200
    except Exception as e:
        # If an error occurs, rollback the transaction
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# Route to update existing cluster data
@app.route('/api/cluster/<id>', methods=["PUT", "PATCH"])
@cross_origin()  # Enable CORS on this route
def update_cluster(id):
    # Extract data from the request body
    data = request.get_json()

    # Extract new name and workspaces from the data
    new_name = data.get('name')
    new_workspaces = data.get('workspaces')

    # Retrieve the cluster from the database
    cluster = MyTable.query.get(id)
    
    if cluster:
        # Update the cluster with the new data
        if new_name:
            cluster.name = new_name
        if new_workspaces:
            cluster.workspaces = new_workspaces
        
        try:
            # Commit the changes to the database
            db.session.commit()
            return jsonify({'message': 'Cluster updated successfully'}), 200
        except Exception as e:
            # If an error occurs, rollback the transaction
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Cluster not found'}), 404


# Route to delete a cluster
@app.route('/api/cluster/<id>', methods=["DELETE"])
@cross_origin()  # Enable CORS on this route
def delete_cluster(id):
    # Retrieve the cluster from the database
    cluster = MyTable.query.get(id)

    if cluster:
        try:
            # Delete the cluster from the database
            db.session.delete(cluster)
            # Commit the changes
            db.session.commit()
            return jsonify({'message': 'Cluster deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Cluster not found'}), 404
    


@app.route('/api/users', methods=['GET'])
@cross_origin()  # Enable CORS on this route
def fetch_users():
    items = UserTable.query.all()  # Fetch all rows from the 'users' table
    result = []
    for item in items:
        row_data = {col: getattr(item, col) for col in item.__table__.columns.keys()}
        result.append(row_data)
    return jsonify(result)  # Returns data as JSON


@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    # Fetch the user by ID
    user = UserTable.query.get(user_id)
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




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  