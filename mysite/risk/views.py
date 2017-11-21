from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

import json

from .forms import StockForm
from .forms import PortfolioForm
from .forms import OptionForm

import pandas_datareader.data as web
import pandas as pd

import plotly.offline as py
import plotly.graph_objs as go

def index(request, version='default'):
    if (version == 'stock'):
        return render_stock(request)
    elif (version == 'portfolio'):
        return render_portfolio(request)
    elif (version == 'option'):
        return render_option(request)
    else:
        return redirect('/risk/stock/')

def render_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].replace(' ','').split(",")
            initial = form.cleaned_data['initial']
            window = form.cleaned_data['window']
            startDate = form.cleaned_data['startDate']
            endDate = form.cleaned_data['endDate']
            varp = form.cleaned_data['varp']
            esp = form.cleaned_data['esp']
            nday = form.cleaned_data['nday']
            method = form.cleaned_data['method']
            plotType = form.cleaned_data['plotType']
            data = dataframe_from_tickerlist(ticker, startDate, endDate)
            if (plotType == "PR"):
                jsonData = plot_historical_price(ticker, data)
            else:
                return redirect('/risk/stock/')
            return render(request, 'risk/index.html', {'plotValue': jsonData, 'version': 'stock'})
    else:
        form = StockForm(initial={'ticker':'AAPL', 'initial':'10000', 'window':'10', 'startDate':'2000-1-1', 'endDate':'2010-12-31', 'varp':'0.99', 'esp':'0.975', 'nday':'5'})
    return render(request, 'risk/index.html', {'stockForm': form, 'version': 'stock'})

def render_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].replace(' ','').split(",")
            # Need check weight
            weight = form.cleaned_data['weight'].replace(' ','').split(",")
            initial = form.cleaned_data['initial']
            window = form.cleaned_data['window']
            startDate = form.cleaned_data['startDate']
            endDate = form.cleaned_data['endDate']
            varp = form.cleaned_data['varp']
            esp = form.cleaned_data['esp']
            nday = form.cleaned_data['nday']
            method = form.cleaned_data['method']
            #data = dataframe_from_tickerlist(ticker, startDate, endDate)
            #jsonData = plot_historical_price(ticker, data)
            #return render(request, 'risk/index.html', {'plot': jsonData})
    else:
        form = PortfolioForm(initial={'ticker':'AAPL', 'weight':'1', 'initial':'10000', 'window':'10', 'startDate':'2000-1-1', 'endDate':'2010-12-31', 'varp':'0.99', 'esp':'0.975', 'nday':'5'})
    return render(request, 'risk/index.html', {'portfolioForm': form, 'version': 'portfolio'})

def render_option(request):
    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].replace(' ','').split(",")
            initial = form.cleaned_data['initial']
            window = form.cleaned_data['window']
            startDate = form.cleaned_data['startDate']
            endDate = form.cleaned_data['endDate']
            varp = form.cleaned_data['varp']
            esp = form.cleaned_data['esp']
            nday = form.cleaned_data['nday']
            method = form.cleaned_data['method']
            #data = dataframe_from_tickerlist(ticker, startDate, endDate)
            #jsonData = plot_historical_price(ticker, data)
            #return render(request, 'risk/index.html', {'plot': jsonData})
    else:
        form = OptionForm(initial={'ticker':'AAPL', 'initial':'10000', 'window':'10', 'startDate':'2000-1-1', 'endDate':'2010-12-31', 'varp':'0.99', 'esp':'0.975', 'nday':'5'})
    return render(request, 'risk/index.html', {'optionForm': form, 'version': 'option'})

#dataframe_from_tickerlist(["AAPL","TSLA"],"2016-01-01","2016-12-31")
def dataframe_from_tickerlist(tickerlist, startDate, endDate):
    data = {}
    for t in tickerlist:
        attempts = 0
        while attempts < 5:
            try:
                data[str.format(t)] = web.DataReader(t, 'yahoo', startDate, endDate)['Adj Close'].rename(t)
                break
            except:
                if (attempts >= 5):
                    raise
                attempts += 1
    data = pd.DataFrame(data)
    return data

# Currently only plot one stock
def plot_historical_price(ticker, data):
    dates = data[ticker].index.tolist()
    dates = [date.strftime("%Y-%m-%d") for date in dates]
    values = data[ticker].values.tolist()
    values = [value[0] for value in values]
    return json.dumps({'x':dates, 'y':values, 'ticker':ticker})

