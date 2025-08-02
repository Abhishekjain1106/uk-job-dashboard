import streamlit as st
import pandas as pd
import boto3

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- AWS and DynamoDB Setup ---
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UK_Jobs')

# --- Caching ---
@st.cache_data(ttl=300)
def fetch_all_jobs():
    """Scans the entire DynamoDB table and returns all items."""
    response = table.scan()
    data = response.get('Items', [])
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response.get('Items', []))
        
    return pd.DataFrame(data)

# --- The App UI ---
st.title("🇬🇧 UK Job Engine Dashboard")
st.write("This dashboard displays all jobs collected by the automated backend.")

# Fetch the data
jobs_df = fetch_all_jobs()

# --- NEW: Add a search filter ---
st.header("🔍 Filter Jobs")
search_term = st.text_input("Search by job title, company, or keyword:")

# --- NEW: Logic to apply the filter ---
if search_term:
    # We filter the DataFrame to only include rows where the 'title' column
    # contains the search term. `case=False` makes it case-insensitive.
    filtered_df = jobs_df[jobs_df['title'].str.contains(search_term, case=False, na=False)]
else:
    # If the search box is empty, show the full dataframe
    filtered_df = jobs_df

st.success(f"Displaying {len(filtered_df)} of {len(jobs_df)} jobs.")

# --- MODIFIED: Display the FILTERED Data Table ---
# We now display the filtered_df instead of the original jobs_df
st.dataframe(filtered_df)
