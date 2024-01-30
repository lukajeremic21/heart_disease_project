import random
from faker import Faker
import pymysql
import os
from dotenv import load_dotenv
load_dotenv()

# Get MySQL connection details from environment variables
mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")

# Initialize Faker
fake = Faker()

# Establish database connection
mysql_connection = pymysql.connect(host=mysql_host,
                                   user=mysql_user,
                                   password=mysql_password,
                                   db=mysql_database)

try:
    with mysql_connection.cursor() as cursor:
        for _ in range(1025):
            # Generate random data
            first_name = fake.first_name()
            last_name = fake.last_name()
            birthdate = fake.date_of_birth(minimum_age=18, maximum_age=90)

            # Prepare SQL query
            sql = "INSERT INTO patients (first_name, last_name, birthdate) VALUES (%s, %s, %s)"

            # Execute SQL query
            cursor.execute(sql, (first_name, last_name, birthdate))

        # Commit the transaction
        mysql_connection.commit()

finally:
    # Close the connection
    mysql_connection.close()