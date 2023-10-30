from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired
app = FastAPI()

templates = Jinja2Templates(directory="templates")

import pandas as pd

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

average_occupancy = round(sum(seasonality_df['occupancy_rates']) / 12, 2)
average_rate = round(sum(seasonality_df['daily_rates']) / 12, 2)


# Define route to render the dashboard template
@app.get("/")
def render_dashboard(request: Request):
    # Here, you can calculate the data points you want to display or pass them directly
    # For now, I'm hardcoding them as an example
    context = {
        "yearly_operating_income": "$27,000",
        "annual_revenue": "$39,000",
        "operating_expenses": "$12,000",
        "expected_breakeven": "4 years"
    }
    return templates.TemplateResponse("dashboard.html", {"request": request, **context})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
