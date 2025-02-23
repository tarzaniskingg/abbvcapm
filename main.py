import streamlit as st
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title('AbbVie Inc. Capital Asset Pricing Model and Beta')

timemap = {0: "Daily", 1:"Weekly", 2:"Monthly"}
timeselection = st.pills("Frequency", options=timemap.keys(), format_func=lambda x: timemap[x], selection_mode="single")
if timeselection == 0:
    rangemap = {0: "6 months", 1: "1 year", 2: "2 years", 3: "5 years"}
elif timeselection == 1:
    rangemap = {0: "6 months", 1:"1 year", 2: "2 years"}
elif timeselection == 2:
    rangemap = {0: "6 months", 1: "1 year"}
else:
    rangemap = {0: "6 months", 1: "1 year", 2: "2 years", 3: "5 years"}
rangeselection = st.pills("Range", options=rangemap.keys(), format_func=lambda x: rangemap[x], selection_mode="single")
weekly = pd.read_csv('rawweekly.csv')
weekly['Dates'] = pd.to_datetime(weekly['Dates'])
weekly.set_index('Dates', inplace=True)
weekly.sort_index(inplace=True)
endog = weekly['ABBV']
exog = sm.add_constant(weekly['SPX'])
weeklywindow = {0: 52, 1: 104, 2:260}
model = RollingOLS(endog, exog, window=weeklywindow[rangeselection]).fit()

weekly['Rolling Beta'] = model.params['SPX']
weekly_beta = weekly.dropna()
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=weekly_beta.index,
    y=weekly_beta['Rolling Beta'],
    mode='lines',
    name='Rolling Beta'
))

# Lock the zoom and disable panning
fig.update_layout(
    title="Beta Over Time",
    xaxis=dict(fixedrange=True),  # Lock zoom for x-axis
    yaxis=dict(fixedrange=False),  # Lock zoom for y-axis
    dragmode=False  # Prevent zooming and panning
)

# Display locked chart in Streamlit
st.plotly_chart(fig, use_container_width=True)








mrp = st.slider("What is your Market Risk Premium?", 0.0, 10.0, 4.0, 0.1)
timehorizon = st.select_slider("What is your investment horizon?", options = ["3M", "6M", "1Y", "2Y", "3Y", "5Y"])
time_horizons = {
    '3M': 13,  # ~13 weeks forward
    '6M': 26,  # ~26 weeks forward
    '1Y': 52,  # ~52 weeks forward
    '2Y': 104, # ~104 weeks forward
    '3Y': 156, # ~156 weeks forward
    '5Y': 260  # ~260 weeks forward
}
weekly['ER'] = weekly['Rolling Beta'] * mrp/100 + weekly['10Y Yield']/100
weekly['RR'] = weekly['ABBVP'].pct_change(periods=time_horizons[timehorizon]).shift(-time_horizons[timehorizon])
weekly_sliced = weekly.dropna()

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=weekly_sliced.index,
    y=weekly_sliced['ER'],
    mode='lines',
    name='Expected Return'
))
fig2.add_trace(go.Scatter(
    x=weekly_sliced.index,
    y=weekly_sliced['RR'],
    mode='lines',
    name='Realised Return'
))
# Lock the zoom and disable panning
fig2.update_layout(
    title="Expected Return vs Annualised Return Over Time",
    xaxis=dict(fixedrange=False),  # Lock zoom for x-axis
    yaxis=dict(tickformat = "1%", fixedrange=True),  # Lock zoom for y-axis
    dragmode=False,  # Prevent zooming and panning
    legend = dict(
        x=0.75,  # Position legend inside the chart (left side)
        y=0.98,  # Near the top
        bgcolor="rgba(255,255,255,0.6)",  # Semi-transparent white background
        bordercolor="black",
        borderwidth=1
    )
)

# Display locked chart in Streamlit
st.plotly_chart(fig2, use_container_width=True, key = fig2)