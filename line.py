import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# Plotting the styled line chart
fig, ax = plt.subplots()

# Plot the main line connecting all points in chronological order
ax.plot(filtered_data['Date'].values, filtered_data['Severity'].values, marker='o', linestyle='-', color='blue')

# Define color mapping for severity
color_mapping = {1: 'green', 2: 'yellow', 3: 'red'}

# Plot the data points with color mapping
for severity, color in color_mapping.items():
    severity_data = filtered_data[filtered_data['Severity'] == severity]
    ax.scatter(severity_data['Date'].values, severity_data['Severity'].values, color=color, label=f'{severity}', s=100, edgecolor='black')

# Customizing the plot
ax.set_xlabel("Date")
ax.set_ylabel("Severity")
ax.set_title(f"Severity over Time for {selected_farm}")
ax.set_xticks(filtered_data['Date'].values)
ax.set_xticklabels(filtered_data['Date'].dt.strftime('%d/%m/%Y'), rotation=45)
ax.set_yticks([1, 2, 3])
ax.set_yticklabels(['Low', 'Medium', 'High'])

# Adding a legend for the severity levels
severity_labels = {1: 'Low', 2: 'Medium', 3: 'High'}
handles, labels = ax.get_legend_handles_labels()
new_labels = [severity_labels[int(label)] for label in labels]
ax.legend(handles, new_labels)

# Display the plot in Streamlit
st.pyplot(fig)
