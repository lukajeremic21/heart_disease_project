User Manual for Heart Disease Prediction System

1. Introduction <a name="introduction"></a>
Welcome to the Heart Disease Prediction System! This system allows patients to register, log in, and manage their health records. Doctors can also log in, view patient records, and assign patients to specific records.

2. Getting Started <a name="getting-started"></a>
Prerequisites <a name="prerequisites"></a>
Before using the application, ensure you have the following installed:

Python (version 3.6 or higher)
MySQL database
Necessary Python packages (install using pip install -r requirements.txt)
Installation <a name="installation"></a>
Clone the repository:


git clone https://github.com/your_username/heart-disease-prediction.git
cd heart-disease-prediction
Set up a virtual environment (recommended):


python -m venv venv
source venv/bin/activate  # On Windows, use "venv\Scripts\activate"
Install dependencies:

pip install -r requirements.txt
Set up environment variables:

Create a .env file in the project root and define the following variables:


MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_mysql_database
SECRET_KEY=your_secret_key
Run the application:

python main.py
The application will be accessible at http://localhost:5000.

3. Authentication <a name="authentication"></a>
Patient Signup <a name="patient-signup"></a>
To register as a patient:

Endpoint: POST /signup

Payload: JSON with the following fields:

first_name, last_name, birthdate, username, password
Example:


curl -X POST -H "Content-Type: application/json" -d '{"first_name": "John", "last_name": "Doe", "birthdate": "1990-01-01", "username": "john_doe", "password": "password123"}' http://localhost:5000/signup
Patient Login <a name="patient-login"></a>
To log in as a patient:

Endpoint: POST /login

Payload: JSON with the following fields:

username, password
Example:


curl -X POST -H "Content-Type: application/json" -d '{"username": "john_doe", "password": "password123"}' http://localhost:5000/login
Doctor Login <a name="doctor-login"></a>
To log in as a doctor:

Endpoint: POST /doctor_login

Payload: JSON with the following fields:

username, password
Example:


curl -X POST -H "Content-Type: application/json" -d '{"username": "dr_smith", "password": "dr_password"}' http://localhost:5000/doctor_login
4. Endpoints <a name="endpoints"></a>
1. Get Heart Disease Data <a name="1-get-heart-disease-data"></a>
Endpoint: GET /getHeartDiseaseData
Description: Get heart disease data for all patients.
2. Get Heart Disease Data for a Specific Patient <a name="2-get-heart-disease-data-for-a-specific-patient"></a>
Endpoint: GET /getHeartDiseaseData/<int:patient_id>
Description: Get heart disease data for a specific patient.
3. Delete Heart Disease Data <a name="3-delete-heart-disease-data"></a>
Endpoint: DELETE /deleteHeartDiseaseData/<int:patient_id>
Description: Delete heart disease data for a specific patient.
4. Get Average Age <a name="4-get-average-age"></a>
Endpoint: GET /getAverageAge
Description: Get the average age of patients.
5. Get Max Trestbps <a name="5-get-max-trestbps"></a>
Endpoint: GET /getMaxTrestbps
Description: Get the maximum and minimum Trestbps values.
6. Insert Heart Disease Data <a name="6-insert-heart-disease-data"></a>
Endpoint: POST /insertHeartDiseaseData
Payload: JSON with heart disease data fields.
Description: Insert new heart disease data.
7. Get Doctor Records <a name="7-get-doctor-records"></a>
Endpoint: GET /doctor_records
Description: Get heart disease records assigned to the logged-in doctor.
8. Upload Excel File and Insert Data <a name="8-upload-excel-file-and-insert-data"></a>
Endpoint: POST /uploadExcelAndInsert
Payload: Excel file with heart disease data.
Description: Upload an Excel file and insert data into the database.
9. Train Logistic Regression Model <a name="9-train-logistic-regression-model"></a>
Endpoint: GET /trainModel
Description: Train a logistic regression model on historical heart disease data.
10. Train Naive Bayes Model <a name="10-train-naive-bayes-model"></a>
Endpoint: GET /trainNaiveBayes
Description: Train a Naive Bayes model on historical heart disease data.
