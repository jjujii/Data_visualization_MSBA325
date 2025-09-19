import streamlit as st
import pandas as pd
import plotly.graph_objects as go


st.title('Road Quality and Transportation in Lebanon')

data= pd.read_csv("https://linked.aub.edu.lb/pkgcube/data/0050f2ea95d565d42df3600a32193531_20240905_183009.csv")
data_load_state = st.text('Loading data...')
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
  st.write(data.head(20))


def group_main_road_quality_by_governorate(data):
  data['AreaName'] = data['refArea'].apply(lambda x: x.split('/')[-1].replace('_', ' '))
  df_governorates = data[data['AreaName'].str.contains('Governorate')]
  df_governorates['AreaLabel'] = df_governorates['AreaName']
  road_quality_cols = [
    'State of the main roads - good',
    'State of the main roads - acceptable',
    'State of the main roads - bad'
  ]

  for col in road_quality_cols:
    df_governorates[col] = pd.to_numeric(df_governorates[col], errors='coerce')
  grouped = df_governorates.groupby('AreaLabel')[road_quality_cols].mean().reset_index()
  return grouped


st.subheader("Main Road Quality Distribution by Governorate")

main_road_quality = group_main_road_quality_by_governorate(data)
st.write("Values represent the proportion of towns reporting each road condition.")
st.dataframe(main_road_quality)
st.bar_chart(main_road_quality.set_index('AreaLabel'))

transport_cols = [
    'Existence of dedicated bus stops - exists',
    'The main means of public transport - vans',
    'The main means of public transport - taxis',
    'The main means of public transport - buses'
]
bad = data[data["State of the main roads - bad"] == 1][transport_cols].mean()
acceptable = data[data["State of the main roads - acceptable"] == 1][transport_cols].mean()
good = data[data["State of the main roads - good"] == 1][transport_cols].mean()

road_conditions = ['Bad', 'Acceptable', 'Good']
bus_availability = [bad['The main means of public transport - buses'],
                    acceptable['The main means of public transport - buses'],
                    good['The main means of public transport - buses']]
van_availability = [bad['The main means of public transport - vans'],
                    acceptable['The main means of public transport - vans'],
                    good['The main means of public transport - vans']]
taxi_availability = [bad['The main means of public transport - taxis'],
                     acceptable['The main means of public transport - taxis'],
                     good['The main means of public transport - taxis']]
road_conditions = ['Bad', 'Acceptable', 'Good']
transport_data = pd.DataFrame({
    'Buses': bus_availability,
    'Vans': van_availability,
    'Taxis': taxi_availability
}, index=road_conditions)

st.divider()
st.write("Acceptable road quality is the most common across governorates. "
         "We deduce that Baalbek-Hermel Governorate has very few roads with good road quality")
st.divider()
st.subheader("Transport Availability by Road Condition")
fig = go.Figure(data=[
    go.Bar(name='Buses', x=road_conditions, y=bus_availability, marker_color='#FFFF00',
           text=[f"{val * 100:.0f}%" for val in bus_availability], textposition='auto'),
    go.Bar(name='Vans', x=road_conditions, y=van_availability, marker_color='#808080',
           text=[f"{val * 100:.0f}%" for val in van_availability], textposition='auto'),
    go.Bar(name='Taxis', x=road_conditions, y=taxi_availability, marker_color ='#FF0000',
            text=[f"{val * 100:.0f}%" for val in taxi_availability], textposition='auto')])

fig.update_layout(
    title="Transport Availability by Road Condition",
    xaxis_title="Road Quality",
    yaxis_title="Proportion of Towns",
    yaxis=dict(tickformat=".0%"),
    barmode='group'
)

threshold = st.slider("Minimum transport availability (%)", min_value=0, max_value=100, value=30)
threshold /= 100

filtered_bus = [val if val >= threshold else 0 for val in bus_availability]
filtered_van = [val if val >= threshold else 0 for val in van_availability]
filtered_taxi = [val if val >= threshold else 0 for val in taxi_availability]
fig = go.Figure(data=[
    go.Bar(name='Buses', x=road_conditions, y=filtered_bus, marker_color='#FFFF00',
           text=[f"{val * 100:.0f}%" if val > 0 else "" for val in filtered_bus], textposition='auto'),
    go.Bar(name='Vans', x=road_conditions, y=filtered_van, marker_color='#808080',
           text=[f"{val * 100:.0f}%" if val > 0 else "" for val in filtered_van], textposition='auto'),
    go.Bar(name='Taxis', x=road_conditions, y=filtered_taxi, marker_color='#FF0000',
           text=[f"{val * 100:.0f}%" if val > 0 else "" for val in filtered_taxi], textposition='auto')
])
st.plotly_chart(fig)

st.divider()
st.write("The grouped bar chart displays the types of transport available on main roads. We can deduce that which taxis and buses have higher avaialbility when road quality increases (positive relationship), vans become less available as road quality increases (negative relationship)")