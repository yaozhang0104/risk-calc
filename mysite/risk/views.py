from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

import json
from datetime import datetime
import dateutil.relativedelta

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
            
            if (plotType == "PV"):
                rollingdata = rollingdata_from_tickerlist(ticker, window, endDate)
                pricedata = positionprice_from_tickerlist(ticker, startDate)
                sharelist = calculate_share(initial,pricedata,ticker)
                pv = calculate_portfolio_value(ticker,sharelist,rollingdata)
                jsonData = plot_portfolio_value(pv)
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


def rollingdata_from_tickerlist(tickerlist, window, endDate):
    startDate = endDate-dateutil.relativedelta.relativedelta(years = window)
    startDate = startDate.strftime("%Y-%m-%d")
    return dataframe_from_tickerlist(tickerlist, startDate, endDate)

def positionprice_from_tickerlist(tickerlist, positionDate):
    endDate = positionDate+dateutil.relativedelta.relativedelta(days = 10)
    endDate = endDate.strftime("%Y-%m-%d")
    data = dataframe_from_tickerlist(tickerlist, positionDate, endDate)
    return data.head(1)

#dataframe_from_tickerlist(["AAPL","TSLA"],"2016-1-31","2016-12-31")
def dataframe_from_tickerlist(tickerlist, startDate, endDate):
    data = {}
    for t in tickerlist:
        attempts = 0
        while attempts < 5:
            try:
                data[str.format(t)] = web.DataReader(t, 'yahoo', startDate, endDate)['Adj Close'].rename(t)
                break
            except:
                if (attempts >= 4):
                    raise
                attempts += 1
    data = pd.DataFrame(data)
    return data

def calculate_share(initial, pricedata, tickerlist, weightlist=[1]):
    if (len(tickerlist) != len(weightlist)):
        raise ValueError('Ticker and weight length mismatch.')
    share = {}
    i = 0
    for t in tickerlist:
        share[t] = float(weightlist[i])*float(initial)/float(pricedata[t][0])
        i = i+1
    return share

def calculate_portfolio_value(tickerlist, sharelist, rollingdata): 
    pv = pd.DataFrame()
    for t in tickerlist: 
        if (pv.empty):
            pv = rollingdata[t]*sharelist[t]
        else:
            pv = pv + rollingdata[t]*sharelist[t]
    return pv
    
def plot_portfolio_value(data):
    dates = data.index.tolist()
    dates = [date.strftime("%Y-%m-%d") for date in dates]
    values = data.values.tolist()
    return json.dumps({'x':dates, 'y':values, 'info':'Portfolio Value'})

