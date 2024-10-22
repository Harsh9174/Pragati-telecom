import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime

users = {
    "Alice": {"password": "alice123", "role": "Marketing"},
    "Bob": {"password": "bob123", "role": "Marketing"},
    "Charlie": {"password": "charlie123", "role": "Shop"},
    "Diana": {"password": "diana123", "role": "Shop"},
    "admin_user": {"password": "admin123", "role": "Admin"},
}

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='pragati_telecom',
            user='root',
            password='Harsh@9174'
        )
        return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None
    
def insert_data(retailer_name, retailer_phone, product_name, retailer_address, employee_name, date_entered):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            sql_query = """
                INSERT INTO Replacement_info 
                (Retailer_name, Retailer_phone, Product_name, Retailer_address, Employee_name, Dateentered) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            data_tuple = (retailer_name, retailer_phone, product_name, retailer_address, employee_name, date_entered)
            cursor.execute(sql_query, data_tuple)
            connection.commit()
            st.success("Data inserted successfully!")
        except Error as e:
            st.error(f"Error inserting data: {e}")
        finally:
            cursor.close()
            connection.close()

# Function to capitalize names
def capitalize_name(name):
    return ' '.join(word.capitalize() for word in name.split())

# Function for the Marketing Staff data entry page
def marketing_data_entry():
    st.title("Marketing Staff Data Entry")

    with st.form(key='data_entry_form'):
        retailer_name = st.text_input("Retailer Name")
        retailer_phone = st.text_input("Retailer Phone", max_chars=10)
        product_name = st.text_input("Product Name")
        retailer_address = st.text_area("Retailer Address")
        employee_name = st.text_input("Employee Name")
        date_entered = st.date_input("Date Entered", value=datetime.today())

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            # Capitalize the names
            retailer_name = capitalize_name(retailer_name)
            employee_name = capitalize_name(employee_name)

            insert_data(retailer_name, retailer_phone, product_name, retailer_address, employee_name, date_entered)

# Function for the login page
def login_page():
    st.title("Login Page")

    # Create a form for login
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        submit_button = st.form_submit_button("Login")

    # Check if the user wants to log in
    if submit_button:
        # Check if the username exists
        if username in users and users[username]["password"] == password:
            st.session_state["role"] = users[username]["role"]  # Set user role in session state
            st.session_state["logged_in"] = True  # Set logged in status
            st.success(f"Logged in as {username}")
            st.experimental_rerun()  # Refresh the app to show the main content
        else:
            st.error("Invalid username or password")

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    login_page()
else:
    # If logged in, display the main application
    col1, col2 = st.columns([1, 4])

    # Add logo in the first column
    with col1:
        st.image("A:\Pragati_Telecom\.venv\Application\WhatsApp Image 2024-10-22 at 23.41.52_ece6d38f.jpg", width=100)

    # Add title in the second column, aligned to the left
    with col2:
        st.markdown("<h1 style='color: black;'>Pragati Telecom</h1>", unsafe_allow_html=True)

    # Create a left navigation menu with buttons in sidebar
    st.sidebar.title("Navigation")

    # Display pages based on user role
    if st.session_state["role"] == "Admin":
        PAGES = {
            "Marketing Staff": marketing_data_entry,
            "Shop Staff": lambda: st.write("Shop Staff Content"),  # Placeholder for Shop Staff
            "Admin": lambda: st.write("Admin Content"),  # Placeholder for Admin
        }
    elif st.session_state["role"] == "Marketing":
        PAGES = {
            "Marketing Staff": marketing_data_entry,
        }
    elif st.session_state["role"] == "Shop":
        PAGES = {
            "Shop Staff": lambda: st.write("Shop Staff Content"),  # Placeholder for Shop Staff
        }

    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]
    page()
