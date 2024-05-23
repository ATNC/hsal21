import mysql.connector
from mysql.connector import Error
import time
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def create_connection(host_name, user_name, user_password, db_name, port):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            port=port
        )
        print('Connection to MySQL DB successful')
    except Error as e:
        print(f'The error "{e}" occurred')
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query executed successfully')
    except Error as e:
        print(f'The error "{e}" occurred')


def create_table_if_not_exists(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS replication_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        value INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_query(connection, create_table_query)


def main():
    master_connection = create_connection(
        os.getenv('DB_HOST', 'localhost'),
        os.getenv('MYSQL_USER'),
        os.getenv('MYSQL_PASSWORD'),
        os.getenv('MYSQL_DATABASE'),
        int(os.getenv("DB_MASTER_PORT"))
    )
    create_table_if_not_exists(master_connection)

    while True:
        # Generate random data
        value = random.randint(1, 100)
        query = f'INSERT INTO replication_table (value) VALUES ({value})'

        # Execute query on master
        if master_connection:
            execute_query(master_connection, query)

        # Optionally, execute query on slaves (generally not recommended for replication setups)
        # if slave1_connection:
        #     execute_query(slave1_connection, query)
        # if slave2_connection:
        #     execute_query(slave2_connection, query)

        time.sleep(5)  # Wait for 5 seconds before writing the next entry


if __name__ == '__main__':
    main()
