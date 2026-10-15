import pymysql

# Database connection credentials configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kimerayvonne622',  # Replace with your actual MySQL password
    'database': 'sales_management_db',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    """
    Creates and returns a new connection to the MySQL database 
    using the predefined configuration dictionary.
    """
    return pymysql.connect(**DB_CONFIG)