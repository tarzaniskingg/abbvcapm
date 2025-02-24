import streamlit as st
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title('AbbVie Inc. Capital Asset Pricing Model and Beta')

indexmap = {0: "SPX", 1:"NASDAQ", 2:"DJI"}
indexselection = st.pills("Index", options=indexmap.keys(), format_func=lambda x: indexmap[x], selection_mode="single", default= 0)
timemap = {0: "Daily", 1:"Weekly", 2:"Monthly"}
timeselection = st.pills("Frequency", options=timemap.keys(), format_func=lambda x: timemap[x], selection_mode="single", default= 1)
rangemap = {0: "6 months", 1: "1 year", 2: "2 years", 3: "5 years"}
if timeselection == 0:
    weekly = pd.read_csv('rawdaily.csv')
elif timeselection == 1:
    weekly = pd.read_csv('rawweekly.csv')
elif timeselection == 2:
    weekly = pd.read_csv('rawmonthly.csv')
rangeselection = st.pills("Regression Range", options=rangemap.keys(), format_func=lambda x: rangemap[x], selection_mode="single", default=1)
weekly['Dates'] = pd.to_datetime(weekly['Dates'], format = '%d/%m/%Y')
weekly.set_index('Dates', inplace=True)
weekly.sort_index(inplace=True)
endog = weekly['ABBV']
exog = sm.add_constant(weekly[indexmap[indexselection]])
if timeselection == 0:
    weeklywindow = {0: 126, 1: 252, 2: 252*2, 3:252*5}
elif timeselection == 1:
    weeklywindow = {0: 26, 1: 52, 2: 104, 3: 52*5}
elif timeselection == 2:
    weeklywindow = {0: 6, 1: 12, 2: 24, 3: 12*5}
model = RollingOLS(endog, exog, window=weeklywindow[rangeselection]).fit()
weekly['Rolling Beta'] = model.params[indexmap[indexselection]]
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

if timeselection == 1:
    time_horizons = {
        '3M': 13,  # ~13 weeks forward
        '6M': 26,  # ~26 weeks forward
        '1Y': 52,  # ~52 weeks forward
        '2Y': 104, # ~104 weeks forward
        '3Y': 156, # ~156 weeks forward
        '5Y': 260  # ~260 weeks forward
    }
elif timeselection == 0:
    time_horizons = {
        '3M': 63,  # ~13 weeks forward
        '6M': 126,  # ~26 weeks forward
        '1Y': 252,  # ~52 weeks forward
        '2Y': 512, # ~104 weeks forward
        '3Y': 252*3, # ~156 weeks forward
        '5Y': 252*5  # ~260 weeks forward
    }
elif timeselection == 2:
    time_horizons = {
        '3M': 3,  # ~13 weeks forward
        '6M': 6,  # ~26 weeks forward
        '1Y': 12,  # ~52 weeks forward
        '2Y': 24,  # ~104 weeks forward
        '3Y': 36,  # ~156 weeks forward
        '5Y': 60  # ~260 weeks forward
    }
irr_horizons = {
    '3M': 1/4,  # ~13 weeks forward
    '6M': 1/2,  # ~26 weeks forward
    '1Y': 1,  # ~52 weeks forward
    '2Y': 2,  # ~104 weeks forward
    '3Y': 3,  # ~156 weeks forward
    '5Y': 5  # ~260 weeks forward

}

weekly['10Y Yield'] = ((weekly['10Y Yield']/100 + 1) ** irr_horizons[timehorizon]) - 1
mrp = ((mrp/100+1) ** irr_horizons[timehorizon])-1
weekly['ER'] = weekly['Rolling Beta'] * mrp + weekly['10Y Yield']
weekly['RR'] = weekly['ABBVP'].pct_change(periods=time_horizons[timehorizon]).shift(-time_horizons[timehorizon])
weekly['RR'] = ((weekly['RR'] + 1) ** (1/irr_horizons[timehorizon])) - 1

weekly_sliced = weekly.dropna()
fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=weekly_sliced.index,
    y=weekly_sliced['ER'],
    mode='lines',
    name='Expected Return'
))

fig3.add_trace(go.Scatter(
    x=weekly_sliced.index,
    y=weekly_sliced['10Y Yield'],
    mode='lines',
    name='Risk-free Rate'
))

# Lock the zoom and disable panning
fig3.update_layout(
    title="Expected Return Over Time",
    xaxis=dict(fixedrange=False),  # Lock zoom for x-axis
    yaxis=dict(tickformat = "1%", fixedrange=True),  # Lock zoom for y-axis
    dragmode=False,  # Prevent zooming and panning
    legend = dict(
        x=0.90,  # Position legend inside the chart (left side)
        y=0.98,  # Near the top
        bgcolor="rgba(255,255,255,0.6)",  # Semi-transparent white background
        bordercolor="black",
        borderwidth=1
    )
)

# Display locked chart in Streamlit
st.plotly_chart(fig3, use_container_width=True, key = fig3)

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
    title="Expected Return vs Realised Return Over Time",
    xaxis=dict(fixedrange=False),  # Lock zoom for x-axis
    yaxis=dict(tickformat = "1%", fixedrange=True),  # Lock zoom for y-axis
    dragmode=False,  # Prevent zooming and panning
    legend = dict(
        x=0.90,  # Position legend inside the chart (left side)
        y=0.98,  # Near the top
        bgcolor="rgba(255,255,255,0.6)",  # Semi-transparent white background
        bordercolor="black",
        borderwidth=1
    )
)

# Display locked chart in Streamlit
st.plotly_chart(fig2, use_container_width=True, key = fig2)
date = st.date_input("Enter a historical date", min_value = weekly_sliced.index.min(), max_value = weekly_sliced.index.max(), format = "DD/MM/YYYY")
date = pd.Timestamp(date)
nearest_date = weekly_sliced.index.asof(date)
st.latex(r"r_i = r_{RF} + (r_M - r_{RF}) * b_i")
st.write(f"Nearest Date: {nearest_date.strftime('%d/%m/%Y')}")
st.write(f"Expected Return: {weekly_sliced.loc[nearest_date, 'ER']:.2%}")
st.write(f"Risk Free Rate: {weekly_sliced.loc[nearest_date, '10Y Yield']:.2%}")
st.write(f"Market Risk Premium: {mrp:.2%}")
st.write(f"Beta: {weekly_sliced.loc[nearest_date, 'Rolling Beta']:.3}")
st.write(f"Realised Return: {weekly_sliced.loc[nearest_date, 'RR']:.2%}")
expected_return = weekly.loc[nearest_date, 'ER']
realised_return = weekly.loc[nearest_date, 'RR'] if pd.notna(weekly.loc[nearest_date, 'RR']) else None

# Create DataFrame for the bar chart
bar_data = pd.DataFrame({
    "Return Type": ["Expected Return", "Realised Return"],
    "Value": [expected_return, realised_return]
})

# Plot the bar chart in Streamlit
st.bar_chart(bar_data, x="Return Type", y="Value")