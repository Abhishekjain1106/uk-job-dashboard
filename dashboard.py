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
st.write("This dashboard displays all jobs collected by the automated backend, now with AI analysis!")

# Fetch the data
jobs_df = fetch_all_jobs()

# --- NEW: Create filter controls in the sidebar ---
st.sidebar.header("📊 Filters")

# Text search filter
search_term = st.sidebar.text_input("Search by job title:")

# Category filter
# Get a unique list of all categories from our data, and add an 'All' option
all_categories = jobs_df['job_category'].unique()
# Prepend the 'All' option to the list of categories
category_options = ['All'] + list(all_categories)
selected_category = st.sidebar.selectbox("Filter by Job Category:", options=category_options)

# --- Apply filters ---
# Start with the full dataframe
filtered_df = jobs_df

# Apply text search if a term is entered
if search_term:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False)]

# Apply category filter if a specific category is chosen
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['job_category'] == selected_category]

st.success(f"Displaying {len(filtered_df)} of {len(jobs_df)} jobs.")

# --- Display the Data Table with selected columns ---
# We choose which columns to show to keep the table clean
st.dataframe(filtered_df[[
    'title',
    'job_category',
    'key_skills',
    'link',
    'source'
]])
