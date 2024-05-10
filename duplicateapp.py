from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import inspect
from sqlalchemy.sql import text


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure PostgreSQL SQLAlchemy connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://airlinedb_user:AVNS_SFBbzpFCBpvhgbI5M1T@postgres-v1-dbs-do-user-13186796-0.b.db.ondigitalocean.com:25060/airlines_db'  # Replace with your PostgreSQL URI
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
MyTable = Base.classes.booking_matchable

@app.route('/api/data-endpoint', methods=['POST'])
@cross_origin()  # Enable CORS on this route
def fetch_data():
    data = request.get_json()
    column_names = data.get("columns", [])  # Default to empty list
    num_rows = data.get("num_rows", None)
    table_name = data.get("table_name", None)

    if not column_names or num_rows is None:
        # Return error response if required input is missing
        return jsonify({"error": "column_names and num_rows are required"}), 400

    # Create comma-separated string of column names
    column_string = ', '.join(column_names)

    # items = MyTable.query.all()  # Fetch all rows from the table 
    # result = []
    # for item in items:
    #     row_data = {col: getattr(item, col) for col in item.__table__.columns.keys()}  
    #     print(row_data)
    #     result.append(row_data)
    # return jsonify(result)  # Returns data as JSON
    
    
    # Write raw SQL query, replace 'my_table' with your actual table name
    # We are using :num_rows to supply the parameter to the SQL query
    # The fetchall() function fetches all (or all remaining) rows of a query result set and returns a list of tuples.
    query = text(f'SELECT {column_string} FROM {table_name} LIMIT :num_rows')
    print(query)

    result = db.session.execute(query, {"num_rows":num_rows}).fetchall()

    # Convert result (list of tuples) to list of dictionaries
    result_dict = [dict(zip(column_names, row)) for row in result]
    print(result)
    return jsonify(result_dict)


@app.route('/api/metadata/<table_name>', methods=['GET'])
@cross_origin()  # Enable CORS on this route
def get_metadata(table_name):
    inspector = inspect(db.engine)

    # table_name = 'booking_matchable'  # Replace with your table name

    columns = [{'name': c['name'], 'type': str(c['type'])} for c in inspector.get_columns(table_name)]
    row_count = db.session.query(MyTable).count()

    return jsonify({
        'table_name': table_name,
        'columns': columns,
        'row_count': row_count
    })


@app.route('/api/get-table-names', methods=['GET'])
@cross_origin()  # Enable CORS on this route
def get_table_names():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    return jsonify(table_names)



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)  # The app will be accessible at localhost:5000
