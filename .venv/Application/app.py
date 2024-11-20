import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import date


solutions_list = ["Repaired", "Replace", "Return", "OOW", "NOT PT"]  # Replace with actual solutions
emp_list = ["Pratik", "Harsh", "Neeraj", "Saran", "Preeti", "Bhola", "Anshu", "Anshuman", "Suraj", "Anjali"]  # Replace with actual employee names

st.set_page_config(layout="wide")

# Supabase credentials
SUPABASE_URL = "https://ihbcpsdnaxojlhkjlnkx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImloYmNwc2RuYXhvamxoa2psbmt4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIwMjIyODEsImV4cCI6MjA0NzU5ODI4MX0.k4HRprT-kHwst84HL5PNPsVvsgXVGdrbTlMzwx0_cIU"

# Cache the Supabase client
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Supabase client (cached)
supabase: Client = get_supabase_client()

# Function to fetch data from the table
def fetch_data():
    # Fetch the data from the view without retailer_id
    response = supabase.table("repl_info_view").select("job_id, recieved_date, shop_name, shop_address, phone_number, product_name, brand, problem, qty, serial_number, recieved_by, solution, checked_by, send_by, send_date, image").order("recieved_date",desc=True).execute()
    return response.data
# Function to fetch shop names from the database (and make them unique)

def fetch_shop_names():
    response = supabase.table("repl_info_view").select("shop_name", "shop_address", "phone_number").order("shop_name").execute()

    # Assuming the first element of the response is the result data (a list of rows)
    rows = response.data if response.data else []

    # Use a dictionary where each shop_name has its own dictionary with all three fields
    shop_names =  {row['shop_name']: (row['shop_address'], row['phone_number']) for row in rows} if rows else {}
    
    return shop_names

def insert_data(data):
    response = supabase.table("replacement_info").insert([data]).execute()
    return response

def fetch_records_by_date(recieved_date):

    formatted_date = recieved_date.strftime('%Y-%m-%d')

    response = supabase.table("repl_info_view").select("*").eq("recieved_date", formatted_date).execute()
    return response.data  # Return all records if the query was successful

def update_record(retailer_id, serial_number,solution, checked_by, send_by, send_date):
    # Prepare the update data
    update_data = {
        "serial_number": serial_number,
        "solution": solution,
        "checked_by": checked_by,
        "send_by": send_by,
        "send_date": send_date
    }
    
    # Update the record in the database
    response = supabase.table("replacement_info").update(update_data).eq("retailer_id", retailer_id).execute()
    return response

def data_export():
    """Render the Admin Data Export page."""
    data = fetch_data()
    if data:
        df = pd.DataFrame(data)
        if not df.empty:
        # Create an Excel file from the DataFrame
            excel_file = "Replacement_info_data.xlsx"
            df.to_excel(excel_file, index=False)

        # Provide download button
            with open(excel_file, "rb") as file:
                st.download_button(label="Download Excel", data=file, file_name=excel_file, key="download_excel")
        else:
            st.warning("No data available to export.")
    else:
        st.warning("No data available to export.")

# Page title
st.markdown(
    """
    <style>
    .logo-title-container {
        display: flex;
        align-items: left;
        justify-content: flex-start;
        flex-wrap: wrap;
    }
    .logo-container {
        flex: 0 0 100px;
        margin-right: 10px;
    }
    .title-container {
        flex: 1;
    }
    @media (max-width: 768px) {
        .logo-title-container {
            justify-content: center;
            text-align: center;
        }
        .logo-container {
            margin: 0 auto 10px auto;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="logo-title-container">
        <div class="logo-container">
            <img src="https://i.postimg.cc/1txpDNCc/Whats-App-Image-2024-10-22-at-23-41-52-ece6d38f.jpg" width="100">
        </div>
        <div class="title-container">
            <h1 style='color: black; font-size: 35px; font-weight: bold;'>Pragati Telecom</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.title("Replacement Data Entry")


action = st.radio("Select Action:", ("Add New Record", "Edit Existing Record", "Search Records"), horizontal=True)

if action == "Add New Record":

# Create the form
    with st.expander("Add New Record", expanded=True):
        # Dropdown to select shop name or add new shop
        Recieved_date = st.date_input("Received date", key="add_date")
        
        existing_shops = fetch_shop_names()
        shop_names = list(existing_shops.keys())

        selected_shop_name = st.selectbox("Select Existing Shop Name or Enter New", ["🏪Add Shop➕"] + shop_names, key="add_name", index=None)

        if selected_shop_name == "🏪Add Shop➕":
            Shop_name = st.text_input("Enter New Shop Name", key="new_shop_name")
            Shop_address = st.text_input("Shop Address", key="add_address")
            phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)

        elif selected_shop_name is not None:
                
            Shop_address, phone_number = existing_shops[selected_shop_name]  
            Shop_name = selected_shop_name
            Shop_address = st.text_input("Shop Address", value=Shop_address, key="add_address", disabled=False)  
            phone_number = st.text_input("Retailer Phone (Numeric Only)", value=str(phone_number), key="add_phone", disabled=False)
        else:
            Shop_name = ""
            Shop_address = st.text_input("Shop Address", key="add_address")
            phone_number = st.text_input("Retailer Phone (Numeric Only)", key="add_phone", max_chars=10)


        Product_name = st.text_input("Product Name", key="add_product")
        Quantity = st.number_input("Quantity",key= "add_qty",step=1,min_value=1)
        Serial_Number = st.text_input("Serial Number", key="add_serial")
        Brand = st.text_input("Brand", key="add_brand")
        Problem = st.text_input("Problem (Mandatory)", key="add_problem")  # Make it clear this is mandatory
        Recieved_by = st.selectbox("Received By", emp_list, key="add_recby", index=None)

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
                try:
            # Insert data into the table with empty fields for others
                    data = {
                "recieved_date": str(Recieved_date),  # Convert to string for Supabase
                "shop_name": Shop_name.title().strip(),
                "shop_address": Shop_address.title().strip(),
                "phone_number": phone_number,
                "product_name": Product_name.title().strip(),
                "brand": Brand.title().strip(),
                "problem": Problem.title().strip(),
                "qty": Quantity,
                "serial_number": Serial_Number.title().strip(),
                "recieved_by": Recieved_by
                # Fields not mentioned here will default to NULL in the table
            }
                    insert_data(data)
                    st.success("Data submitted successfully!")
                except Exception as e:
                    st.error(f"Error submitting data: {e}")  # Insert data only if all validations pass
                
elif action == "Edit Existing Record":
    with st.expander("Edit Existing Record", expanded=True):
        selected_date = st.date_input("Select Received Date", key="selected_date")
        
        if selected_date:
            records = fetch_records_by_date(selected_date)
            
            if records:
                retailer_ids = [r['job_id'] for r in records]
                selected_retailer_id = st.selectbox("Select Job ID", retailer_ids, key="edit_retailer_id")
                selected_record = None
                for record in records:
                    if record['job_id'] == selected_retailer_id:
                        selected_record = record
                        break  

                # Step 5: Populate the form fields with data from the selected record
                if selected_record:
                    retailer_id = selected_record['retailer_id']

                    selected_shop_name = st.text_input("Shop Name", value=selected_record['shop_name'], key="edit_shop_name",disabled=True)
                    shop_address = st.text_input("Shop Address", value=selected_record['shop_address'], key="edit_shop_address",disabled=True)
                    phone = st.text_input("Phone (Numeric Only)", value=str(selected_record['phone_number']), key="edit_phone",disabled=True)
                    product_name = st.text_input("Product Name", value=selected_record['product_name'], key="edit_product_name",disabled=True)
                    brand = st.text_input("Brand", value=selected_record['brand'], key="edit_brand",disabled=True)
                    problem = st.text_input("Problem", value=selected_record['problem'], key="edit_problem",disabled=True)
                    serial_number = st.text_input("Remarks", value=selected_record['serial_number'], key="edit_serial_number")
                    

                    if selected_record['solution'] is None:
                        solution_options = solutions_list  # Use full options if no existing solution
                        solution_index = None  # Default to the first option
                    else:
                        solution_options = [selected_record['solution']] # Add existing solution to options
                        solution_index = solution_options.index(selected_record['solution'])  # Set index to existing solution

                    solution = st.selectbox("Solution", solution_options, index=solution_index, key="edit_solution")
                    
                    if selected_record['checked_by'] is None:
                        checkby_options = emp_list  # Use full options if no existing solution
                        checkby_index = None  # Default to the first option
                    else:
                        checkby_options = [selected_record['checked_by']] # Add existing solution to options
                        checkby_index = checkby_options.index(selected_record['checked_by'])  # Set index to existing solution

                    checked_by = st.selectbox("Checked By", checkby_options, index=checkby_index, key="edit_checkby")


                    if selected_record['send_by'] is None:
                        sendby_options = emp_list
                        sendby_index = None
                    else:
                        sendby_options = [selected_record['send_by']]
                        sendby_index = sendby_options.index(selected_record['send_by'])

                    send_by = st.selectbox("Send by", sendby_options,index=sendby_index, key="edit_send_by")

                    send_date = st.date_input("Send Date", value=None, key="edit_send_date")
                
                if st.button("Update", key="edit_submit"):
                    try:
                        send_date_str = str(send_date) if send_date else None
                        update_record(retailer_id,serial_number,solution,checked_by,send_by,send_date_str)
                        st.success("Data submitted successfully!")
                    except Exception as e:
                        st.error(f"Error submitting data: {e}")    # Update data only if valid
            else:
                st.warning("No records found for the selected date.")


elif action == "Search Records":
    with st.expander("Search Records", expanded=True):
        # Search input (either phone number or shop name or address)
        search_term = st.text_input("Enter Phone Number, Shop Name, or Address", key="search_term")

        # Add a search button below the input bar
        if st.button("🔍 Search", key="search_button"):
            if search_term:
                # Fetch all the data (you might need to filter it based on your data source)
                data = fetch_data()

                # Filter the data based on search term (search in phone_number, shop_name, and shop_address)
                filtered_data = [record for record in data if (
                    search_term.lower() in str(record['phone_number']).lower() or
                    search_term.lower() in record['shop_name'].lower() or
                    search_term.lower() in record['shop_address'].lower()
                )]
                
                # Check if filtered data is found
                if filtered_data:
                    # Display the filtered data (you can use a dataframe or just print the records)
                    st.write(f"Found {len(filtered_data)} record(s) matching '{search_term}'")
                    
                    # Optionally, display the filtered data in a nice table format (you can also use st.dataframe)
                    st.dataframe(filtered_data)  # Display as a table
                    
                else:
                    st.warning("No records found matching the search term.")
            else:
                st.warning("Please enter a search term to search records.")


st.header("Data Preview")
data = fetch_data()
if data:
    st.dataframe(data)  # Display the data in a table
else:
    st.write("No data found in the table.")

data_export()
