from flask import Flask, request, jsonify, session
import pandas as pd
import os
from dotenv import load_dotenv
import mysql.connector
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from flasgger.utils import swag_from

# Load environment variables from .env file
load_dotenv()

# Get MySQL connection details from environment variables
mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")
secret_key = os.getenv("SECRET_KEY")



# Create Flask app
app = Flask(__name__)
app.secret_key = secret_key
swagger = Swagger(app)

# Set the SQLALCHEMY_DATABASE_URI using the environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"

# Other SQLAlchemy configurations (if needed)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create SQLAlchemy instance
db = SQLAlchemy(app)

# Connect to MySQL host
mysql_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database
)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250))
    last_name = db.Column(db.String(250))
    birthdate = db.Column(db.Date)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)


class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    password_hash = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/signup', methods=['POST'])
@swag_from('swagger/signup.yml')
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_patient = Patient(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        birthdate=data.get('birthdate'),
        username=data['username'],
        password=hashed_password
    )
    db.session.add(new_patient)
    db.session.commit()
    session['patient_id'] = new_patient.id
    return jsonify({'message': 'Registered successfully'}), 201


@app.route('/login', methods=['POST'])
@swag_from('swagger/login.yml')
def login():
    data = request.get_json()
    patient = Patient.query.filter_by(username=data['username']).first()
    if patient and check_password_hash(patient.password, data['password']):
        session['patient_id'] = patient.id
        return jsonify({'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/measurments', methods=['GET'])
@swag_from('swagger/measurments.yml')
def get_measurments():
    patient_id = session.get('patient_id')
    if patient_id is None:
        return jsonify({'message': 'Not logged in'}), 401

    cursor = mysql_connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT patients.first_name, patients.last_name, heartdiseasedata.*
        FROM heartdiseasedata
        LEFT JOIN patients ON heartdiseasedata.patient_id = patients.id
        WHERE patients.id = %s
    """, (patient_id,))
    data = cursor.fetchall()
    cursor.close()

    if not data:
        return jsonify({"error": "Patient not found"}), 404

    return jsonify(data)


@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    patient_id = session.get('patient_id')
    if patient_id is None:
        return jsonify({'message': 'Not logged in'}), 401

    data = request.get_json()
    record_id = data.get('record_id')
    doctor_id = data.get('doctor_id')

    cursor = mysql_connection.cursor()
    cursor.execute("""
        UPDATE heartdiseasedata
        SET doctor_id = %s
        WHERE id = %s AND patient_id = %s
    """, (doctor_id, record_id, patient_id))
    mysql_connection.commit()
    cursor.close()

    return jsonify({'message': 'Doctor id added successfully'}), 200


# Define routes
@app.route('/')
def hello():
    return 'Dobrodošli!'

@app.route('/getHeartDiseaseData', methods=['GET'])
def get_heart_disease_data():
    cursor = mysql_connection.cursor(dictionary=True)  # Use dictionary cursor to fetch results with column names
    cursor.execute("""
        SELECT patients.first_name, patients.last_name, heartdiseasedata.*
        FROM heartdiseasedata
        LEFT JOIN patients ON heartdiseasedata.patient_id = patients.id
    """)
    
    data = cursor.fetchall()
    cursor.close()

    # Format the result with first_name and last_name at the beginning of each object
    formatted_data = [{"name": f"{row['first_name']} {row['last_name']}", **row} for row in data]

    return jsonify(formatted_data)

@app.route('/getHeartDiseaseData/<int:patient_id>', methods=['GET'])
def get_heart_disease_data_patient(patient_id):
    cursor = mysql_connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT patients.first_name, patients.last_name, heartdiseasedata.*
        FROM heartdiseasedata
        LEFT JOIN patients ON heartdiseasedata.patient_id = patients.id
        WHERE patients.id = %s
    """, (patient_id,))
    
    data = cursor.fetchall()
    cursor.close()

    if not data:
        return jsonify({"error": "Patient not found"}), 404

    formatted_data = [{"name": f"{row['first_name']} {row['last_name']}", **row} for row in data]

    return jsonify(formatted_data)


@app.route('/deleteHeartDiseaseData/<int:patient_id>', methods=['DELETE'])
def delete_heart_disease_data(patient_id):
    cursor = mysql_connection.cursor()

    # Assuming 'your_table' is the name of your MySQL table
    query = "DELETE FROM your_table WHERE patient_id = %s"
    cursor.execute(query, (patient_id,))
    mysql_connection.commit()

    cursor.close()

    return jsonify({"message": "Record deleted successfully"})


@app.route('/getAverageAge', methods=['GET'])
def get_average_age():
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT AVG(age) FROM heartdiseasedata")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@app.route('/getMaxTrestbps', methods=['GET'])
def get_max_trestbps():
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT MAX(trestbps), MIN(trestbps) FROM heartdiseasedata")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route('/insertHeartDiseaseData', methods=['POST'])
def insert_heart_disease_data():
    data = request.get_json()

    cursor = mysql_connection.cursor()

    # Assuming 'your_table' is the name of your MySQL table
    insert_query = """
        INSERT INTO heartdiseasedata
        (patient_id, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data['patient_id'],
        data['age'],
        data['sex'],
        data['cp'],
        data['trestbps'],
        data['chol'],
        data['fbs'],
        data['restecg'],
        data['thalach'],
        data['exang'],
        data['oldpeak'],
        data['slope'],
        data['ca'],
        data['thal'],
        data['target']
    )

    cursor.execute(insert_query, values)

    # Commit the changes to the database
    mysql_connection.commit()

    cursor.close()

    return jsonify({"message": "Record inserted successfully"})


def insert_data_to_mysql(data):
    cursor = mysql_connection.cursor()

    # Assuming 'your_table' is the name of your MySQL table
    insert_query = """
        INSERT INTO heartdiseasedata
        (patient_id, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for index, row in data.iterrows():
        # Convert data types if needed
        values = tuple(row.values)
        cursor.execute(insert_query, values)

    # Commit the changes to the database
    mysql_connection.commit()

    cursor.close()

@app.route('/doctor_login', methods=['POST'])
def doctor_login():
    data = request.get_json()
    doctor = Doctor.query.filter_by(username=data['username']).first()
    if doctor and check_password_hash(doctor.password, data['password']):
        session['doctor_id'] = doctor.id
        return jsonify({'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/doctor_records', methods=['GET'])
def get_doctor_records():
    doctor_id = session.get('doctor_id')
    if doctor_id is None:
        return jsonify({'message': 'Not logged in'}), 401

    cursor = mysql_connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT heartdiseasedata.*
        FROM heartdiseasedata
        WHERE heartdiseasedata.doctor_id = %s
    """, (doctor_id,))
    data = cursor.fetchall()
    cursor.close()

    if not data:
        return jsonify({"error": "No records found"}), 404

    return jsonify(data)

@app.route('/uploadExcelAndInsert', methods=['POST'])
def upload_excel_and_insert():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    # Check if the file has a name and is an Excel file
    if file.filename == '' or not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Invalid file format. Please provide an Excel file (.xlsx or .csv)"}), 400

    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file)

        # Insert data into MySQL
        insert_data_to_mysql(df)

        return jsonify({"success": "Data inserted successfully"})
    except Exception as e:
        return jsonify({"error": f"Error processing the file: {str(e)}"}), 500
    
@app.route('/trainModel', methods=['GET'])
def train_model():
    try:
        cursor = mysql_connection.cursor()
        cursor.execute("SELECT age, sex, cp, trestbps, chol, thalach, target FROM heartdiseasedata")
        data = cursor.fetchall()
        cursor.close()

        # Convert data to DataFrame
        df = pd.DataFrame(data, columns=['age', 'sex', 'cp', 'trestbps', 'chol', 'thalach', 'target'])
        
        # Assume that 'target' is the column we want to predict
        X = df[['age', 'sex', 'cp', 'trestbps', 'chol', 'thalach']]  # Features
        y = df['target']  # Target variable

        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create and train the model
        model = LogisticRegression()
        model.fit(X_train, y_train)

        # Make predictions and calculate accuracy
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        response_message = {
            "message": "Model Training Successful",
            "accuracy": round(accuracy, 2),
            "interpretation": "The logistic regression model has been successfully trained on historical data. The accuracy of the model, representing its ability to predict heart disease based on selected features, is {}%. This indicates a strong performance in distinguishing between individuals with and without heart disease.".format(round(accuracy * 100, 2))
        }
        return jsonify(response_message)
    except Exception as e:
        return jsonify({"error": f"Error training the model: {str(e)}"}), 500
    

@app.route('/trainNaiveBayes', methods=['GET'])
def train_naive_bayes():
    try:
        cursor = mysql_connection.cursor()
        cursor.execute("SELECT age, trestbps, chol, thalach, target FROM heartdiseasedata")
        data = cursor.fetchall()
        cursor.close()

        # Convert data to DataFrame
        df = pd.DataFrame(data, columns=['age', 'trestbps', 'chol', 'thalach', 'target'])

        # Encode the target variable 'target' (assuming 0 for no heart disease, 1 for heart disease)
        df['target'] = df['target'].map({0: 0, 1: 1})

        # Assume that 'target' is the column we want to predict
        X = df[['age', 'trestbps', 'chol', 'thalach']]  # Features
        y = df['target']  # Target variable

        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create and train the model
        model = GaussianNB()
        model.fit(X_train, y_train)

        # Make predictions and calculate accuracy
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        response_message = {
            "message": "Naive Bayes Training Successful",
            "accuracy": round(accuracy, 2),
            "interpretation": "The Naive Bayes model has been successfully trained on historical data. The accuracy of the model, representing its ability to predict heart disease based on selected features, is {}%. This indicates a strong performance in distinguishing between individuals with and without heart disease.".format(round(accuracy * 100, 2))
        }
        return jsonify(response_message)
    except Exception as e:
        return jsonify({"error": f"Error training the Naive Bayes model: {str(e)}"}), 500

    

if __name__ == '__main__':
    app.run()