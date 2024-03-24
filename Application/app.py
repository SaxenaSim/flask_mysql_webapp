from flask import Flask, render_template,request,redirect,url_for
import mysql.connector
import logging, logging.config
import yaml

app = Flask(__name__,static_folder='static')

with open("configurations/config.yaml", 'r') as file:
    config = yaml.safe_load(file)


DB_HOST = config['database']['host']
DB_PORT = config['database']['port']
DB_DATABASE = config['database']['database']
DB_USER = config['database']['user']
DB_PASSWORD = config['database']['password']

# Database credentials
# DB_HOST = '127.0.0.1'
# DB_PORT = 3306
# DB_DATABASE = 'company'
# DB_USER = 'root'
# DB_PASSWORD = 'India@123'

# Create connection string
#connection_string = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

with open("configurations/logging_config.yaml","r") as f:
    logging_config=yaml.safe_load(f)

logging.config.dictConfig(logging_config)
logger=logging.getLogger("file_logger")

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/table')
def display_table():
    try:
        logger.debug("Entered display_table method")
        # Establish database connection
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_DATABASE,
                                       user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Execute SQL queries
        cursor.execute("SELECT * FROM details")
        data = cursor.fetchall()
        logger.debug(f"data from details table: {data}")
        cursor.execute("SHOW COLUMNS FROM details")
        columns = [column[0] for column in cursor.fetchall()]
        logger.debug(f"columns of the table: {columns}")
        # Close cursor and connection
        cursor.close()
        conn.close()

        return render_template('table.html', data=data, columns=columns)
    except Exception as e:
        logger.debug(f"Error occured in display_table method: {e}")
        # Handle exceptions
        return f"An error occurred: {e}", 500
    
@app.route('/edit/<string:emp_code>', methods=['GET', 'POST'])
def edit_row(emp_code):
    try:
        logger.debug("Entered into edit_row method")
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_DATABASE,
                                       user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM details WHERE emp_code = %s", (emp_code,))
        row_data = cursor.fetchone()
        logger.debug(f"Particular row to be edited:{row_data}")

        if request.method == 'POST':
            logger.debug("it is a post request")
            new_data = {key: request.form[key] for key in request.form}
            update_query = "UPDATE details SET "
            update_query += ", ".join([f"{key} = '{new_data[key]}'" for key in new_data])
            update_query += f" WHERE emp_code = '{emp_code}'"
            logger.debug(f"query to update data:{update_query}")
            cursor.execute(update_query)
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('display_table'))
        else:
            return render_template('edit_form.html', row_data=row_data, emp_code=emp_code)
    except Exception as e:
        logger.debug(f"error occured in edit method : {e}")
        return f"An error occurred: {e}", 500
    
@app.route('/add_column', methods=['GET', 'POST'])
def add_column():
    try:
        logger.debug("entered into add_column method")
        if request.method == 'POST':
            column_name = request.form['column_name']
            data_type = request.form['data_type']
            
            # Print or log the SQL query for debugging
            sql_query = f"ALTER TABLE details ADD COLUMN {column_name} {data_type}"
            logger.debug(f"SQL Query: {sql_query}")  # Print the SQL query
            
            # Establish database connection
            conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, database=DB_DATABASE,
                                           user=DB_USER, password=DB_PASSWORD)
            cursor = conn.cursor()
            
            # Execute SQL query to add column
            cursor.execute(sql_query)
            conn.commit()
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            # Redirect to the table display page
            return redirect(url_for('display_table'))
        else:
            # If GET request, render the add column form
            return render_template('add_column.html')
    except Exception as e:
        logger.error(f"An error occurred while adding a new column: {e}")
        return f"An error occurred while adding a new column: {e}", 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)

# from flask import Flask, render_template
# from flask_mysqldb import MySQL

# app = Flask(__name__)
# mysql = MySQL(app)

# # MySQL Configuration
# app.config['MYSQL_HOST'] ='127.0.0.1'
# app.config['MYSQL_PORT']= 3306
# app.config['MYSQL_DATABASE_DB'] = 'company'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'India@123'
# #mysql.init_app(app)

# # Routes
# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/table')
# def display_table():
#     conn = mysql.connection
#     cursor = conn.cursor()
#     cursor.execute("USE company")
#     cursor.execute("SELECT * FROM details")
#     print("..............")
#     data = cursor.fetchall()
#     print(data)
#     cursor.execute("SHOW COLUMNS FROM details")
#     columns=[column[0] for column in cursor.fetchall()]
#     print(columns)
#     cursor.close()
#     conn.close()
#     return render_template('table.html', data=data, columns=columns)

# if __name__ == '__main__':
#     app.run(debug=True)