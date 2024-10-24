import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd
import boto3
import uuid
from botocore.exceptions import NoCredentialsError


AWS_ACCESS_KEY_ID = 'AKIA5G2VGK6DHWFGIG4G'  # Replace with your AWS Access Key ID
AWS_SECRET_ACCESS_KEY = 'jt1revT2nkG3UDt9qY9EXmgm4Z0SRRfLPV7HkFIi'  # Replace with your AWS Secret Access Key
AWS_BUCKET_NAME = 'pragati-telecom'  # Replace with your S3 bucket name
AWS_REGION = 'eu-north-1'  # e.g., 'us-east-1'

# Initialize a session using Boto3
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

s3_client = session.client('s3')

def upload_to_s3(file, bucket_name, object_name):
    """Upload a file to an S3 bucket."""
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
    except NoCredentialsError:
        st.error("Credentials not available")
        return None


# Global variables for connection details
DB_CONFIG = {
    "host": "ptdb.c9gi2240g4xb.eu-north-1.rds.amazonaws.com",
    "user": "admin",
    "password": "0R7l0rFh2swBGC9M9YMR",
    "database": "pragati_telecom",
}

# Predefined lists for dropdowns
solutions_list = ["Repaired", "Replace", "Return", "OOW", "NOT PT"]
emp_list = ["Pratik", "Harsh", "Neeraj", "Saran", "Preeti", "Bhola", "Anshu", "Anshuman", "Suraj"]

def create_connection():
    """Create a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"The error '{e}' occurred")
    return None

def execute_query(sql_query, data=None, fetch=False):
    """Execute a query with optional data and return results if fetch is True."""
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if data:
                cursor.execute(sql_query, data)
                if fetch:
                    rows = cursor.fetchall()
                    return pd.DataFrame(rows) if rows else pd.DataFrame()
                else:
                    conn.commit()
                    st.success("Operation successful!")
            else:
                cursor.execute(sql_query)
                if fetch:
                    rows = cursor.fetchall()
                    return pd.DataFrame(rows) if rows else pd.DataFrame()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

def insert_data(data):
    """Insert data into the Replacement_info table."""
    sql_query = """
        INSERT INTO Replacement_info 
        (Recieved_date, Shop_name, Shop_address, phone_number, Product_name, Brand, Problem, Recieved_by, Solution, Checked_by, Send_by, serial_number, Send_date, image) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, NULL, NULL, %s, NULL, %s)
    """
    execute_query(sql_query, data)

def fetch_data():
    """Fetch data from the Replacement_info table."""
    sql_query = """
        SELECT concat('PT_', Retailer_id) as Job_ID, Recieved_date, Shop_name, Shop_address, phone_number, Product_name, 
        Brand, Problem, Recieved_by, serial_number, Solution, Checked_by, Send_by, Send_date, image 
        FROM Replacement_info
    """
    return execute_query(sql_query, fetch=True)

def update_data(retailer_id, data):
    """Update an existing record in the Replacement_info table."""
    sql_query = """
        UPDATE Replacement_info 
        SET Solution=%s, Checked_by=%s, Send_by=%s, Send_date=%s 
        WHERE Retailer_id=%s
    """
    execute_query(sql_query, (*data, retailer_id))

def fetch_data_by_date(selected_date):
    """Fetch data based on selected date."""
    sql_query = "SELECT * FROM Replacement_info WHERE Recieved_date = %s"
    return execute_query(sql_query, (selected_date,), fetch=True)

def admin_data_export():
    """Export data to an Excel file."""
    df = fetch_data()
    if not df.empty:
        excel_file = "Replacement_info_data.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as file:
            st.download_button(label="Download Excel", data=file, file_name=excel_file, key="download_excel")
    else:
        st.warning("No data available to export.")

def fetch_shop_names():
    """Fetch existing shop names, addresses, and phone numbers."""
    sql_query = "SELECT DISTINCT Shop_name, Shop_address, phone_number FROM Replacement_info ORDER BY Shop_name"
    rows = execute_query(sql_query, fetch=True)
    if not rows.empty:
        return {row['Shop_name']: (row['Shop_address'], row['phone_number']) for row in rows.to_dict(orient='records')}
    return {}


col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://i.postimg.cc/1txpDNCc/Whats-App-Image-2024-10-22-at-23-41-52-ece6d38f.jpg", width=100)
with col2:
    st.markdown("<h1 style='color: black; font-size: 30px; font-weight: bold;'>Pragati Telecom</h1>", unsafe_allow_html=True)

# Data management section
st.title("Replacement Data Entry")

# Create radio buttons for selecting action (Add or Edit)
action = st.radio("Select Action:", ("Add New Record", "Edit Existing Record", "Search Records"), horizontal=True)

existing_shop_names = fetch_shop_names()

if action == "Add New Record":
    with st.expander("Add New Record", expanded=True):
        Recieved_date = st.date_input("Received date", key="add_date")
        
        # Fetch existing shop names along with addresses and phone numbers
        existing_shops = fetch_shop_names()
        shop_names = list(existing_shops.keys())
        

        # Create a selectbox for existing shop names
        selected_shop_name = st.selectbox("Select Existing Shop Name or Enter New", ["🏪Add Shop➕"] + shop_names, key="add_name", index=None)

        # If "Add Shop" is selected, allow manual entry
        if selected_shop_name == "🏪Add Shop➕":
            Shop_name = st.text_input("Enter New Shop Name", key="new_shop_name")
            Shop_address = st.text_input("Shop Address", key="add_address")
            phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)

        elif selected_shop_name is not None:
            # Get address and phone for the selected shop
            Shop_address, phone_number = existing_shops[selected_shop_name]  # Get address and phone for the selected shop
            Shop_name = selected_shop_name
            Shop_address = st.text_input("Shop Address", value=Shop_address, key="add_address", disabled=False)  # Disable manual editing
            phone_number = st.text_input("Retailer Phone (Numeric Only)", value=str(phone_number), key="add_phone", disabled=False)  # Disable manual editing
        else:
            # If nothing is selected, display empty fields
            Shop_name = ""
            Shop_address = st.text_input("Shop Address", key="add_address")
            phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)


        Product_name = st.text_input("Product Name", key="add_product")
        Serial_Number = st.text_input("Serial Number", key="add_serial")
        Brand = st.text_input("Brand", key="add_brand")
        Problem = st.text_input("Problem (Mandatory)", key="add_problem")  # Make it clear this is mandatory
        Recieved_by = st.selectbox("Received By", emp_list, key="add_recby", index=None)

        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}.jpg"  # You can change the extension based on your image type

            # Upload to S3
                

    if st.button("Submit", key="add_submit"):
        # Validate inputs
        if not phone_number.isdigit() or len(phone_number) != 10:
            st.warning("Please enter a valid 10-digit phone number.")
        elif not Problem.strip():
            st.warning("Please enter a valid problem description.")
        elif not Shop_name.strip():
            st.warning("Please enter a valid shop name.")
        elif Recieved_by is None:
            st.warning("Please select who received the product.")
        else:
            image_link = upload_to_s3(uploaded_file, AWS_BUCKET_NAME, unique_filename)
            data = (
                Recieved_date,
                Shop_name.strip().title(),
                Shop_address.strip().title(),
                phone_number.strip(),
                Product_name.strip().title(),
                Brand.strip().title(),
                Problem.strip().title(),
                Recieved_by,
                Serial_Number.strip().title(),
                image_link
            )
            insert_data(data)  # Insert data only if all validations pass

elif action == "Edit Existing Record":
    with st.expander("Edit Existing Record", expanded=True):
        selected_date = st.date_input("Select Received Date", key="selected_date")

        if selected_date:
            # Fetch records for the selected date
            df = fetch_data_by_date(selected_date)

            if not df.empty:
                # Create a dropdown to select an existing Retailer ID based on the selected date
                retailer_ids = df['Retailer_id'].unique()
                formatted_retailer_ids = [f"PT_{id_}" for id_ in retailer_ids]  # Format retailer IDs
                selected_retailer_id = st.selectbox("Select Job ID", formatted_retailer_ids, key="edit_retailer_id")

                # Get the actual Retailer ID from the formatted selection
                actual_retailer_id = selected_retailer_id.split("_")[1]  # Extract the actual ID

                # Filter the dataframe by the actual Retailer ID
                record_df = df[df['Retailer_id'].astype(str) == actual_retailer_id]

                if not record_df.empty:
                    # Fetch the selected record details
                    selected_record = record_df.iloc[0]

                    # Create text inputs and dropdowns for the rest of the fields
                    selected_shop_name = st.text_input("Shop Name", value=selected_record['Shop_name'], key="edit_shop_name")
                    shop_address = st.text_input("Shop Address", value=selected_record['Shop_address'], key="edit_shop_address")
                    phone = st.text_input("Phone (Numeric Only)", value=str(selected_record['phone_number']), key="edit_phone")
                    product_name = st.text_input("Product Name", value=selected_record['Product_name'], key="edit_product_name")
                    brand = st.text_input("Brand", value=selected_record['Brand'], key="edit_brand")
                    problem = st.text_input("Problem", value=selected_record['Problem'], key="edit_problem")
                    serial_number = st.text_input("Serial Number", value=selected_record['serial_number'], key="edit_serial_number")

                    if selected_record['Solution'] is None:
                        solution_options = solutions_list  # Use full options if no existing solution
                        solution_index = None  # Default to the first option
                    else:
                        solution_options = [selected_record['Solution']] # Add existing solution to options
                        solution_index = solution_options.index(selected_record['Solution'])  # Set index to existing solution

                    solution = st.selectbox("Solution", solution_options, index=solution_index, key="edit_solution")
                    

                    if selected_record['Checked_by'] is None:
                        checkby_options = emp_list  # Use full options if no existing solution
                        checkby_index = None  # Default to the first option
                    else:
                        checkby_options = [selected_record['Checked_by']] # Add existing solution to options
                        checkby_index = checkby_options.index(selected_record['Checked_by'])  # Set index to existing solution

                    checked_by = st.selectbox("Checked By", checkby_options, index=checkby_index, key="edit_checkby")

                    # if selected_record['Send_by'] is None:
                    #     sendby_options = emp_list  # Use full options if no existing value
                    #     sendby_index = 0  # Default to the first option
                    # else:
                    #     sendby_options = emp_list  # Use full options

                    #     if selected_record['Send_by'] in sendby_options:
                    #         sendby_index = sendby_options.index(selected_record['Send_by'])  # Set index to existing value
                    #     else:
                    #         sendby_index = 0  # Default to the first option if existing value is not found

                    send_by = st.selectbox("Send by", emp_list,index=None, key="edit_send_by")

                    # send_by = st.selectbox("Send by", sendby_options, index=sendby_index, key="edit_send_by")

                    send_date = st.date_input("Send Date", value=None, key="edit_send_date")

                    if st.button("Update", key="edit_submit"):
                        # Prepare updated data, checking if fields are empty
                        updated_data = (
                            solution,
                            checked_by,
                            send_by,
                            send_date
                        )
                        # Update the record using the actual Retailer ID
                        update_data(actual_retailer_id, updated_data)  # Update data only if valid
            else:
                st.warning("No records found for the selected date.")

                
elif action == "Search Records":
    with st.expander("Search Records", expanded=True):
        # Search input (either phone number or shop name)
        search_term = st.text_input("Enter Phone Number or Shop Name", key="search_term")

        # Add a search button below the input bar
        if st.button("🔍 Search", key="search_button"):
            if search_term:
                # Fetch the entire data
                df = fetch_data()

                # Check if the search term is numeric (indicating a phone number) or not (indicating a shop name)
                if search_term.isdigit():
                    # Search by phone number
                    search_results = df[df['phone_number'].astype(str).str.contains(search_term)]
                else:
                    # Search by shop name
                    search_results = df[df['Shop_name'].str.contains(search_term, case=False)]

                # Display the search results
                if not search_results.empty:
                    st.write(f"Found {len(search_results)} records matching '{search_term}':")
                    st.dataframe(search_results)
                else:
                    st.warning(f"No records found for '{search_term}'")
            else:
                st.warning("Please enter a search term.")

# Display Data after buttons
st.header("Replacement Data")
df = fetch_data()
st.dataframe(df)

# Always show the download button since we've removed the login logic
admin_data_export()
