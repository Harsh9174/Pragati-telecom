import streamlit as st
import pymysql
import pandas as pd

solutions_list = ["Repaired", "Replace", "Return", "OOW", "NOT PT"]  # Replace with actual solutions
emp_list = ["Pratik", "Harsh", "Neeraj", "Saran", "Preeti", "Bhola", "Anshu", "Anshuman", "Suraj"]  # Replace with actual employee names

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
                    (Recieved_date, Shop_name, Shop_address, phone_number, Product_name, Brand, Problem, Recieved_by, Solution, Checked_by, Send_by, Send_date, image) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '', '', '', NULL, '')
                """
                cursor.execute(sql_query, data)
                conn.commit()
                st.success("Data inserted successfully!")

def fetch_data():
    """Fetch data from the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Replacement_info")
                rows = cursor.fetchall()
                return pd.DataFrame(rows) if rows else pd.DataFrame()  # Return an empty DataFrame if no rows

def update_data(retailer_id, data):
    """Update an existing record in the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                sql_query = """
                    UPDATE Replacement_info 
                    SET Solution=%s, Checked_by=%s, Send_by=%s, Send_date=%s 
                    WHERE Retailer_id=%s
                """
                cursor.execute(sql_query, (*data, retailer_id))
                conn.commit()
                st.success("Data updated successfully!")

def fetch_data_by_date(selected_date):
    """Fetch data from the Replacement_info table based on selected date."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                sql_query = "SELECT * FROM Replacement_info WHERE Recieved_date = %s"
                cursor.execute(sql_query, (selected_date,))
                rows = cursor.fetchall()
                return pd.DataFrame(rows) if rows else pd.DataFrame()

def admin_data_export():
    """Render the Admin Data Export page."""
    df = fetch_data()
    
    if not df.empty:
        # Create an Excel file from the DataFrame
        excel_file = "Replacement_info_data.xlsx"
        df.to_excel(excel_file, index=False)

        # Provide download button
        with open(excel_file, "rb") as file:
            st.download_button(label="Download Excel", data=file, file_name=excel_file, key="download_excel")
    else:
        st.warning("No data available to export.")

def format_text(input_text):
    """Format the input text: trim whitespace and capitalize.""" 
    return input_text.strip().title() 

col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://i.postimg.cc/1txpDNCc/Whats-App-Image-2024-10-22-at-23-41-52-ece6d38f.jpg", width=100)
with col2:
    st.markdown("<h1 style='color: black;'>Pragati Telecom</h1>", unsafe_allow_html=True)

# Data management section
st.title("Replacement Data Entry")

# Create radio buttons for selecting action (Add or Edit)
action = st.radio("Select Action:", ("Add New Record", "Edit Existing Record"), horizontal=True)

if action == "Add New Record":
    with st.expander("Add New Record", expanded=True):
        Recieved_date = st.date_input("Recieved date", key="add_date")
        Shop_name = st.text_input("Shop Name", key="add_name")
        Shop_address = st.text_input("Shop Address", key="add_address")
        phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)
        Product_name = st.text_input("Product Name", key="add_product")
        Brand = st.text_input("Brand", key="add_brand")
        Problem = st.text_input("Problem (Mandatory)", key="add_problem")  # Make it clear this is mandatory
        Recieved_by = st.selectbox("Recieved By", emp_list, key="add_recby")

    if st.button("Submit", key="add_submit"):
        # Validate inputs
        if not Problem.strip() and not Shop_name.strip() and (not phone_number.isdigit() or len(phone_number) != 10):  # Check if Problem is empty
            st.warning("Please enter a valid phone number and problem.")
        else:
            data = (
                Recieved_date,
                format_text(Shop_name),
                format_text(Shop_address),
                format_text(phone_number),
                format_text(Product_name),
                format_text(Brand),
                format_text(Problem),
                format_text(Recieved_by),
            )
            insert_data(data)  # Insert data only if valid

elif action == "Edit Existing Record":
    with st.expander("Edit Existing Record", expanded=True):
        selected_date = st.date_input("Select Recieved Date", key="selected_date")
        
        if selected_date:
            df = fetch_data_by_date(selected_date)
            if not df.empty:
                # Create a dropdown to select an existing record based on the selected date
                record_selection = st.selectbox("Select Record to Edit", df['Retailer_id'].tolist(), key="edit_record")

                # Fetch the selected record details
                selected_record = df[df['Retailer_id'] == record_selection].iloc[0]
                
                # Display fields for editing, pre-filled with selected record data
                Shop_name = st.text_input("Shop Name", value=selected_record['Shop_name'], key="edit_name")
                Shop_address = st.text_input("Shop Name", value=selected_record['Shop_address'], key="edit_address")
                phone = st.text_input("RPhone (Numeric Only)", value=selected_record['phone_number'], key="edit_phone")
                product_name = st.text_input("Product Name", value=selected_record['Product_name'], key="edit_product")
                brand = st.text_input("Brand", value=selected_record['Brand'], key="edit_brand")
                problem = st.text_input("Problem", value=selected_record['Problem'], key="edit_problem")
                Recieved_by = st.text_input("Product Name", value=selected_record['Recieved_by'], key="edit_recieveby")
                Solution = st.selectbox("Solution", solutions_list,key = "Edit_solution")
                Checked_by = st.selectbox("Checked By", emp_list,key = "Edit_checkedby")
                Send_by = st.selectbox("Send By", emp_list,key = "Edit_sendby")
                Send_date = st.date_input("Send date", key="add_senddate")
                
                if st.button("Submit", key="edit_submit"):
                    # Validate inputs
                    if not phone.isdigit() or phone == "":
                        st.warning("Please enter a valid phone number.")
                    else:
                        data = (
                            Solution, 
                            Checked_by, # Keep existing solution for now, update if needed
                            Send_by,
                            Send_date
                        )
                        update_data(record_selection, data)  # Update data only if valid

# Display Data after buttons
st.header("Existing Data")
df = fetch_data()
st.dataframe(df)

# Always show the download button since we've removed the login logic
admin_data_export()
