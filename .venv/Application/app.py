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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '', '', '', %s,%s,NULL, '')
                """
                cursor.execute(sql_query, data)
                conn.commit()
                st.success("Data inserted successfully!")

def fetch_data():
    """Fetch data from the Replacement_info table."""
    with create_connection() as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT Recieved_date, Shop_name, Shop_address, phone_number, Product_name, Brand, Problem, Recieved_by,serial_number,Qty, Solution, Checked_by, Send_by,Send_date, image FROM Replacement_info")
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
    st.markdown("<h1 style='color: black; font-size: 40px; font-weight: bold;'>Pragati Telecom</h1>", unsafe_allow_html=True)

# Data management section
st.title("Replacement Data Entry")

# Create radio buttons for selecting action (Add or Edit)
action = st.radio("Select Action:", ("Add New Record", "Edit Existing Record", "Search Records"), horizontal=True)

if action == "Add New Record":
    with st.expander("Add New Record", expanded=True):
        Recieved_date = st.date_input("Recieved date", key="add_date")
        Shop_name = st.text_input("Shop Name", key="add_name")
        Shop_address = st.text_input("Shop Address", key="add_address")
        phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)
        Product_name = st.text_input("Product Name", key="add_product")
        Serial_Number = st.text_input("Serial Number", key="add_serial")
        qty = st.text_input("Quantity", key="add_qty")
        Brand = st.text_input("Brand", key="add_brand")
        Problem = st.text_input("Problem (Mandatory)", key="add_problem")  # Make it clear this is mandatory
        Recieved_by = st.selectbox("Recieved By",emp_list, key="add_recby",index=None)

    if st.button("Submit", key="add_submit"):
        # Validate inputs
        if not Problem.strip() and not Shop_name.strip() and not phone_number.isdigit() or len(phone_number) != 10:  # Check if Problem is empty
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
                Serial_Number,
                qty
            )
            insert_data(data)  # Insert data only if valid

elif action == "Edit Existing Record":
    with st.expander("Edit Existing Record", expanded=True):
        selected_date = st.date_input("Select Recieved Date", key="selected_date")
        
        if selected_date:
            df = fetch_data_by_date(selected_date)
            if not df.empty:
                # Create a dropdown to select an existing shop name based on the selected date
                shop_names = df['Shop_name'].unique()
                selected_shop = st.selectbox("Select Shop Name", shop_names, key="edit_shop")

                # Filter the dataframe by the selected shop
                shop_df = df[df['Shop_name'] == selected_shop]

                if not shop_df.empty:
                    # Create a dropdown to select the product for the selected shop
                    products = shop_df['Product_name']
                    selected_product = st.selectbox("Select Product", products, key="edit_product")

                    shop_address = df['Shop_address'].unique()
                    Shop_address = st.selectbox("Shop Address", shop_address, key="edit_address")

                    phone = df['phone_number'].unique()
                    phone = st.selectbox("Phone (Numeric Only)", phone, key="edit_phone")

                    # Fetch the selected record details based on both shop name and product name
                    selected_record = shop_df[shop_df['Product_name'] == selected_product].iloc[0]
                    
                    # Display fields for editing, pre-filled with selected record data

                    brand = st.text_input("Brand", value=selected_record['Brand'], key="edit_brand")
                    problem = st.text_input("Problem", value=selected_record['Problem'], key="edit_problem")
                    Recieved_by = st.text_input("Recieved by", value=selected_record['Recieved_by'], key="edit_recieveby")
                    Solution = st.selectbox("Solution", solutions_list, key="edit_solution", index=None)
                    Checked_by = st.selectbox("Checked By", emp_list, key="edit_checkedby", index=None)
                    Send_by = st.selectbox("Send By", emp_list, key="edit_sendby", index=None)
                    Send_date = st.date_input("Send Date", value=selected_record['Send_date'], key="edit_senddate")
                    
                    if st.button("Submit", key="edit_submit"):
                            data = (
                                Solution, 
                                Checked_by, 
                                Send_by,
                                Send_date
                            )
                            update_data(selected_record['Retailer_id'], data)  # Update data only if valid

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
