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
                    (Recieved_date, Shop_name, Shop_address, phone_number, Product_name, Brand, Problem, Recieved_by, Solution, Checked_by, Send_by, serial_number,Qty,Send_date, image) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '', '', '', %s,0,NULL, '')
                """
                cursor.execute(sql_query, data)
                conn.commit()
                st.success("Data inserted successfully!")

def fetch_data():
    """Fetch data from the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT concat('PT_',Retailer_id) as Job_ID,Recieved_date, Shop_name, Shop_address, phone_number, Product_name, Brand, Problem, Recieved_by,serial_number, Solution, Checked_by, Send_by,Send_date, image FROM Replacement_info""")
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


def fetch_shop_names():
    """Fetch existing shop names from the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT Shop_name FROM Replacement_info")
                rows = cursor.fetchall()
                return [row['Shop_name'] for row in rows] if rows else []

col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://i.postimg.cc/1txpDNCc/Whats-App-Image-2024-10-22-at-23-41-52-ece6d38f.jpg", width=100)
with col2:
    st.markdown("<h1 style='color: black; font-size: 40px; font-weight: bold;'>Pragati Telecom</h1>", unsafe_allow_html=True)

# Data management section
st.title("Replacement Data Entry")

# Create radio buttons for selecting action (Add or Edit)
action = st.radio("Select Action:", ("Add New Record", "Edit Existing Record", "Search Records"), horizontal=True)

existing_shop_names = fetch_shop_names()

if action == "Add New Record":
    with st.expander("Add New Record", expanded=True):
        Recieved_date = st.date_input("Received date", key="add_date")
        
        # Create a selectbox for existing shop names
        selected_shop_name = st.selectbox("Select Existing Shop Name or Enter New", ["🏪Add Shop➕"] + existing_shop_names , key="add_name",index = None)

        # If "Other" is selected, allow manual entry
        if selected_shop_name == "🏪Add Shop➕":
            Shop_name = st.text_input("Enter New Shop Name", key="new_shop_name")
        else:
            Shop_name = selected_shop_name

        Shop_address = st.text_input("Shop Address", key="add_address")
        phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)
        Product_name = st.text_input("Product Name", key="add_product")
        Serial_Number = st.text_input("Serial Number", key="add_serial")
        Brand = st.text_input("Brand", key="add_brand")
        Problem = st.text_input("Problem (Mandatory)", key="add_problem")  # Make it clear this is mandatory
        Recieved_by = st.selectbox("Received By", emp_list, key="add_recby", index=None)

    if st.button("Submit", key="add_submit"):
        # Validate inputs
        # Separate checks for each condition
        if not phone_number.isdigit() or len(phone_number) != 10:
            st.warning("Please enter a valid 10-digit phone number.")
        elif not Problem.strip():
            st.warning("Please enter a valid problem description.")
        elif not Shop_name.strip():
            st.warning("Please enter a valid shop name.")
        elif Recieved_by is None:
            st.warning("Please select who received the product.")
        else:
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
            )
            insert_data(data)# Insert data only if all validations pass



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

                    # Select boxes for solution, checked by, and send by
                    solution = st.selectbox("Solution", solutions_list, key="edit_solution", index=None)
                    checked_by = st.selectbox("Checked By", emp_list, key="edit_checked_by", index=None)
                    send_by = st.selectbox("Send By", emp_list, key="edit_send_by", index=None)
                    send_date = st.date_input("Send Date", value=None, key="edit_send_date")

                    if st.button("Update", key="edit_submit"):
                        # Prepare updated data
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
