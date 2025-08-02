import streamlit as st
import pandas as pd
import boto3

# --- Page Configuration ---
# Set the page to use the full screen width
st.set_page_config(layout="wide")

# --- AWS and DynamoDB Setup ---
# This is how we connect to our database
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UK_Jobs')

# --- Caching ---
# @st.cache_data tells Streamlit to "remember" the result of this function.
# It will only re-run the function if 5 minutes have passed (ttl=300 seconds).
# This stops us from hitting our database too often and makes the app fast.
@st.cache_data(ttl=300)
def fetch_all_jobs():
    """Scans the entire DynamoDB table and returns all items."""
    response = table.scan()
    data = response.get('Items', [])
    
    # Keep scanning if the table is large and has more pages of data
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response.get('Items', []))
        
    # Convert the list of jobs into a Pandas DataFrame for easy viewing
    return pd.DataFrame(data)

# --- The App UI ---
st.title("🇬🇧 UK Job Engine Dashboard")
st.write("This dashboard displays all jobs collected by the automated backend.")

# Fetch the data
jobs_df = fetch_all_jobs()

st.success(f"Found a total of {len(jobs_df)} jobs in the database.")

# --- Display the Data Table ---
# st.dataframe is a great way to display data with sorting and scrolling
st.dataframe(jobs_df)
