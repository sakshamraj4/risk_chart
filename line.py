import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import unquote, urlencode

# Function to fetch the CSV data from GitHub
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/sakshamraj4/Abinbav_sustainability/main/risk_level.csv'
    data = pd.read_csv(url)
    return data

# Function to filter unique farm names
def filter_farms(data):
    return data['farmName'].unique()

# Load the data
data = load_data()

# Convert the 'Date' column to datetime format
data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')

# Convert Severity to numerical values for plotting
severity_mapping = {'Low': 1, 'medium': 2, 'high': 3}
data['Severity'] = data['Severity'].map(severity_mapping)

# Get query parameters
query_params = st.experimental_get_query_params()
farm_name_param = query_params.get('farmName', [None])[0]

# Filter unique farm names
farms = filter_farms(data)

# Set the default farm based on query parameter
if farm_name_param:
    farm_name_param = unquote(farm_name_param)
    if farm_name_param in farms:
        default_farm_index = list(farms).index(farm_name_param)
    else:
        default_farm_index = 0
else:
    default_farm_index = 0

# Sidebar for selecting farm name
st.sidebar.title("Farm Name Filter")
selected_farm = st.sidebar.selectbox("Select a farm name:", farms, index=default_farm_index)

# Update query parameters when farm name is selected
params = st.experimental_get_query_params()
params['farmName'] = selected_farm
st.experimental_set_query_params(**params)

# Filter data based on the selected farm name
filtered_data = data[data['farmName'] == selected_farm]

# Main dashboard
st.title(f"Risk Level Monitoring for {selected_farm}")

# Plotting the interactive line chart with Plotly
fig = px.line(
    filtered_data,
    x='Date',
    y='Severity',
    title=f"Severity over Time for {selected_farm}",
    markers=True,
    custom_data=['Note']  # Including the Note column for tooltips
)

# Update the layout to match the desired appearance
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Severity",
    yaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
    xaxis=dict(tickformat='%d/%m/%Y'),
    legend_title="Severity",
    autosize=True,
    height=None,  # Allow height to be responsive
    margin=dict(l=20, r=20, t=40, b=20),
    title={'x': 0.5, 'xanchor': 'center'}
)

# Define the color mapping for scatter plot points
color_mapping = {1: 'green', 2: 'yellow', 3: 'red'}
for severity, color in color_mapping.items():
    fig.add_scatter(
        x=filtered_data[filtered_data['Severity'] == severity]['Date'],
        y=filtered_data[filtered_data['Severity'] == severity]['Severity'],
        mode='markers',
        marker=dict(color=color, size=10, line=dict(color='black', width=1)),
        name={1: 'Low', 2: 'Medium', 3: 'High'}[severity],
        customdata=filtered_data[filtered_data['Severity'] == severity]['Note'],
        hovertemplate='<b>Date:</b> %{x}<br><b>Severity:</b> %{y}<br><b>Note:</b> %{customdata}<extra></extra>'
    )

# Custom CSS to hide Streamlit elements and make the chart full screen
st.markdown(
    """
    <style>
    .css-18e3th9 {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .css-1d391kg, .css-hxt7ib {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
