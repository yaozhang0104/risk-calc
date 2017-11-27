from __future__ import division

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

import json
from datetime import datetime
import dateutil.relativedelta
import numpy as np
from scipy.stats import norm
from scipy.special import ndtri

from .forms import PortfolioForm
from .forms import OptionForm

import pandas_datareader.data as web
import pandas as pd

import plotly.offline as py
import plotly.graph_objs as go

def index(request, version='default'):
    if (version == 'portfolio'):
        return render_portfolio(request)
    elif (version == 'option'):
        return render_option(request)
    else:
        return redirect('/risk/portfolio/')

def render_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].replace(' ','').split(",")
            weight = form.cleaned_data['weight'].replace(' ','').split(",")
            initial = form.cleaned_data['initial']
            rollingWindow = form.cleaned_data['rollingWindow']
            dataWindow = form.cleaned_data['dataWindow']
            startDate = form.cleaned_data['startDate']
            endDate = form.cleaned_data['endDate']
            varp = form.cleaned_data['varp']
            esp = form.cleaned_data['esp']
            nday = form.cleaned_data['nday']
            method = form.cleaned_data['method']
            plotType = form.cleaned_data['plotType']
            
            if (plotType == "PV"):
                rollingdata = rollingdata_from_tickerlist(ticker, dataWindow, endDate)
                pricedata = positionprice_from_tickerlist(ticker, startDate)
                sharelist = calculate_share(initial, pricedata, ticker, weight)
                pv = calculate_portfolio_value(ticker, sharelist, rollingdata)
                jsonData = plot_portfolio(pv)
                return render(request, 'risk/index.html', {'plotValue': jsonData, 'version': 'portfolio', 'title': 'Portfolio Value'})
            elif (plotType == "VAR" and method == "PAR"):
                rollingdata = rollingdata_from_tickerlist(ticker, dataWindow+rollingWindow, endDate)
                pricedata = positionprice_from_tickerlist(ticker, startDate)
                sharelist = calculate_share(initial, pricedata, ticker, weight)
                pv = calculate_portfolio_value(ticker, sharelist, rollingdata)
                gbmData = calculate_nyear_mu_sig(pv, rollingWindow)
                var = calculate_pvar(gbmData, initial, varp, nday)
                jsonData = plot_portfolio(var)
                return render(request, 'risk/index.html', {'plotValue': jsonData, 'version': 'portfolio', 'title': 'Parametric VaR'})
            else:
                return redirect('/risk/portfolio/')
    else:
        form = PortfolioForm(initial={'ticker':'AAPL,MSFT', 'weight':'0.5,0.5','initial':'10000', 'rollingWindow':'5', 'dataWindow':'1', 'startDate':'2016-1-1', 'endDate':'2016-12-31', 'varp':'0.99', 'esp':'0.975', 'nday':'5'})
    return render(request, 'risk/index.html', {'portfolioForm': form, 'version': 'portfolio', 'title': 'Portfolio Value'})

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
    if (isinstance(endDate, str)):
        endDate = datetime.strptime(endDate, "%Y-%m-%d")
    startDate = endDate-dateutil.relativedelta.relativedelta(years = window)
    startDate = startDate.strftime("%Y-%m-%d")
    return dataframe_from_tickerlist(tickerlist, startDate, endDate)

def positionprice_from_tickerlist(tickerlist, positionDate):
    if (isinstance(positionDate, str)):
        positionDate = datetime.strptime(positionDate, "%Y-%m-%d")
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
    pv = pd.DataFrame(pv)
    return pv
    
def plot_portfolio(data):
    dates = data.index.tolist()
    dates = [date.strftime("%Y-%m-%d") for date in dates]
    values = data.values.tolist()
    values = [value[0] for value in values]
    return json.dumps({'x':dates, 'y':values})

def calculate_nyear_mu_sig(data, nyear):
    port_log_return = np.log(data).diff().dropna()
    port_name = list(port_log_return)[0]
    port_len = port_log_return.shape[0]
    nday = int(np.ceil(nyear*252))
    port_log_return["mu"] = np.nan
    port_log_return["sig"] = np.nan
    i = nday-1
    while (i < port_len):
        avg = np.mean(port_log_return[port_name][(i-nday+1):i])
        std = np.sqrt(np.mean(port_log_return[port_name][(i-nday+1):i]**2)-avg**2)
        sig = std*np.sqrt(252)
        mu = avg*252+sig**2/2
        port_log_return["mu"][i] = mu
        port_log_return["sig"][i] = sig
        i = i+1
    return port_log_return.iloc[(nday-1):port_len]
    
def calculate_pvar(data, initial, varp, nday):
    varT = nday/252
    var = pd.DataFrame()
    var['var'] = float(initial)-float(initial)*np.exp(data['sig']*np.sqrt(varT)*norm.ppf(float(1-float(varp)))+(data['mu']-data['sig']**2/2)*varT)
    return var
    
def calculate_pes(data, initial, esp, nday):
    esT = nday/252
    es = pd.DataFrame()
    es['es'] = float(initial)-float(initial)*np.exp(data['mu']*esT)*norm.cdf(norm.ppf(float(1-float(esp)))-data['sig']*np.sqrt(esT))/(1-esp)
    es = pd.DataFrame(es)
    return es
    
    