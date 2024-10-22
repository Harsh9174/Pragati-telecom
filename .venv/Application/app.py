import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime

# User credentials
users = {
    "Alice": {"password": "alice123", "role": "Marketing"},
    "Bob": {"password": "bob123", "role": "Marketing"},
    "Charlie": {"password": "charlie123", "role": "Shop"},
    "Diana": {"password": "diana123", "role": "Shop"},
    "admin_user": {"password": "admin123", "role": "Admin"},
}

def create_connection():
    """Establish a database connection."""
    try:
        return pymysql.connect(
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            db="pragati_telecom",
            host="mysql-387e63d6-harsh-1fc8.g.aivencloud.com",
            password="AVNS_PJRuQlfZ5Ojs_dqCWPX",
            port=20739,
            user="avnadmin",
        )
    except pymysql.Error as e:
        st.error(f"Connection error: {e}")
        return None

def insert_data(data):
    """Insert data into the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                sql_query = """
                    INSERT INTO Replacement_info 
                    (Retailer_name, Retailer_phone, Product_name, Retailer_address, Employee_name, Dateentered) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_query, data)
                conn.commit()
                st.success("Data inserted successfully!")

def capitalize_name(name):
    """Capitalize the first letter of each word in the name."""
    return ' '.join(word.capitalize() for word in name.split())

def marketing_data_entry():
    """Render the Marketing Staff data entry form."""
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
            data = (
                capitalize_name(retailer_name),
                retailer_phone,
                product_name,
                retailer_address,
                capitalize_name(employee_name),
                date_entered,
            )
            insert_data(data)

def fetch_data():
    """Fetch data from the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Replacement_info")
                rows = cursor.fetchall()
                return pd.DataFrame(rows) if rows else pd.DataFrame()  # Return an empty DataFrame if no rows

def admin_data_export():
    """Render the Admin Data Export page."""
    st.title("Admin Data Export")
    df = fetch_data()
    
    if not df.empty:
        st.write("### Data Preview:")
        st.dataframe(df)

        # Create an Excel file from the DataFrame
        excel_file = "Replacement_info_data.xlsx"
        df.to_excel(excel_file, index=False)

        # Provide download button that appears immediately after data is ready
        with open(excel_file, "rb") as file:
            st.download_button(label="Download Excel", data=file, file_name=excel_file, key="download_excel")

    else:
        st.warning("No data available to export.")


placeholder = st.empty()


def login_page():
    """Render the login page."""
    
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        if submit_button and username in users and users[username]["password"] == password:
            
            st.session_state.update({"role": users[username]["role"], "logged_in": True})
            st.success(f"Logged in as {username}")

        else:
            if submit_button:
                st.error("Invalid username or password")

def logout():
    """Clear session state and redirect to the login page."""
    st.session_state.clear()  # Clear session state
    st.success("Logged out successfully!")  # Optional message

# Render the logout button at the top right
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    st.sidebar.button("Logout", on_click=logout)  # Add logout button

if 'logged_in' not in st.session_state:
    login_page()
else:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://i.postimg.cc/1txpDNCc/Whats-App-Image-2024-10-22-at-23-41-52-ece6d38f.jpg", width=100)
    with col2:
        st.markdown("<h1 style='color: black;'>Pragati Telecom</h1>", unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    PAGES = {
        "Marketing Staff": marketing_data_entry,
    }
    if st.session_state["role"] == "Admin":
        PAGES["Admin Data Export"] = admin_data_export
        PAGES["Shop Staff"] = lambda: st.write("Shop Staff Content")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    PAGES[selection]()  # Call the selected page function
