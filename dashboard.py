# Импорт необходимых библиотек (Importing necessary libraries)
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

# data scraped from AirBnb in České Budějovice region
occupancy_rates = [0.267, 0.357, 0.325, 0.487, 0.483, 0.594, 0.74, 0.708, 0.497, 0.562, 0.381, 0.493]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# combined dataframe
seasonal_occupancy = pd.DataFrame({'occupancy_rates': occupancy_rates, 'months': months})

original_daily_rates = [2.9, 3, 3.4, 2.9, 2.8, 2.6, 2.7, 2.75, 2.73, 2.2, 2.1, 3.4]
original_average_rate = 2.5
current_average_rate = 200

current_daily_rates = [original_rate * (current_average_rate / original_average_rate) for original_rate in original_daily_rates]

# Monthly revenue (current rates x days x occupancy)
monthly_revenue = [current_daily_rates[i] * 30 * seasonal_occupancy['occupancy_rates'][i] for i in range(12)]
# Monthly expenses
operating_expenses = 0.3
monthly_expenses = [operating_expenses * monthly_revenue[i] for i in range(12)]
# Monthly net operating income
monthly_net_operating_income = [monthly_revenue[i] - monthly_expenses[i] for i in range(12)]

seasonal_rates = pd.DataFrame({
    'daily_rates': current_daily_rates, 
    'months': months, 
    'monthly_revenue': monthly_revenue, 
    'monthly_expenses': monthly_expenses, 
    'monthly_net_operating_income': monthly_net_operating_income
})

# Округляем до целых чисел
seasonal_rates['daily_rates'] = seasonal_rates['daily_rates'].round(0)
seasonal_rates['monthly_revenue'] = seasonal_rates['monthly_revenue'].round(0)
seasonal_rates['monthly_expenses'] = seasonal_rates['monthly_expenses'].round(0)
seasonal_rates['monthly_net_operating_income'] = seasonal_rates['monthly_net_operating_income'].round(0)

seasonality_df = pd.merge(seasonal_occupancy, seasonal_rates, on='months')
# Set month as the index 
seasonality_df.set_index('months', inplace=True)

Yearly_net_operating_income = sum(seasonality_df['monthly_net_operating_income'])
initial_expenses = 50000
yearly_ROI = round(Yearly_net_operating_income / initial_expenses, 2)
breakeven_months = initial_expenses / (Yearly_net_operating_income / 12)




# Среднее значение занятости и дневной ставки (Average Occupancy and Daily Rate)
average_occupancy = seasonality_df['occupancy_rates'].mean()
average_rate = seasonality_df['daily_rates'].mean()

# Создание графиков (Creating plots)
# График занятости (Occupancy Rate Plot)
occupancy_fig = go.Figure()
occupancy_fig.add_trace(
    go.Scatter(
        x=seasonality_df.index, 
        y=seasonality_df['occupancy_rates'], 
        mode='lines', 
        line=dict(color='magenta', width=4),
        name='Occupancy Rate'
    )
)

# График дневных ставок (Daily Rates Plot)
rates_fig = go.Figure()
rates_fig.add_trace(
    go.Scatter(
        x=seasonality_df.index, 
        y=seasonality_df['daily_rates'], 
        mode='lines', 
        line=dict(color='cyan', width=4),
        name='Daily Rates'
    )
)

# График для Net Operating Income (Net Operating Income Plot)
net_income_fig = go.Figure()
net_income_fig.add_trace(
    go.Scatter(
        x=seasonality_df.index, 
        y=seasonality_df['monthly_net_operating_income'], 
        mode='lines', 
        line=dict(color='blue', width=4),
        name='Net Operating Income'
    )
)

# Инициализация приложения Dash (Initializing the Dash app)
app = dash.Dash(__name__)

# Структура HTML (HTML layout)
app.layout = html.Div([
    html.Div([
        dcc.Graph(figure=net_income_fig, style={'height': '100%'})
    ], style={'width': '60%', 'height': '100%', 'display': 'inline-block'}),
    
    html.Div([
        html.Div([
            dcc.Graph(figure=occupancy_fig, style={'height': '50%'})
        ], style={'height': '50%'}),
        
        html.Div([
            dcc.Graph(figure=rates_fig, style={'height': '50%'})
        ], style={'height': '50%'}),
        
    ], style={'width': '38%', 'height': '100%', 'display': 'inline-block'}),
])

if __name__ == '__main__':
    app.run_server(debug=True)

