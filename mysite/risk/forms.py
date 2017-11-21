from django import forms

class StockForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=5, widget=forms.TextInput(attrs={'class': 'form-control'}))
    initial = forms.DecimalField(label='Initial Investment', widget=forms.TextInput(attrs={'class': 'form-control'}))
    window = forms.IntegerField(label='Rolling Window Length (Year)', max_value=10, min_value=1, widget=forms.TextInput(attrs={'class': 'form-control'}))
    startDate = forms.DateField(label='Position Date', widget=forms.DateInput(attrs={'class': 'form-control'}))
    endDate = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'class': 'form-control'}))
    varp = forms.DecimalField(label='VaR Probability', max_value=0.9999, min_value=0.0001, decimal_places=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    esp = forms.DecimalField(label='ES Probability', max_value=0.9999, min_value=0.0001, decimal_places=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nday = forms.IntegerField(label='N Day Horizon (Day)', max_value=2520, min_value=1, widget=forms.TextInput(attrs={'class': 'form-control'}))
    method = forms.ChoiceField(label='Calculation Method', choices=[('PAR','Parametric'),('HIS','Historical'),('MC','Monte Carlo')], widget=forms.Select(attrs={'class': 'form-control'}))
    plotType = forms.ChoiceField(label='Plot Type', choices=[('PR','Price'),('VAR','Value at Risk (VaR)'),('ES','Expected Shortfall (ES)')], widget=forms.RadioSelect(attrs={'class': 'form-control radio-sel'}))

class PortfolioForm(forms.Form):
    ticker = forms.CharField(label='Ticker List', widget=forms.TextInput(attrs={'class': 'form-control'}))
    weight = forms.CharField(label='Weight List', widget=forms.TextInput(attrs={'class': 'form-control'}))
    initial = forms.DecimalField(label='Initial Investment', widget=forms.TextInput(attrs={'class': 'form-control'}))
    window = forms.IntegerField(label='Rolling Window Length (Year)', max_value=10, min_value=1, widget=forms.TextInput(attrs={'class': 'form-control'}))
    startDate = forms.DateField(label='Position Date', widget=forms.DateInput(attrs={'class': 'form-control'}))
    endDate = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'class': 'form-control'}))
    varp = forms.DecimalField(label='VaR Probability', max_value=0.9999, min_value=0.0001, decimal_places=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    esp = forms.DecimalField(label='ES Probability', max_value=0.9999, min_value=0.0001, decimal_places=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nday = forms.IntegerField(label='N Day Horizon (Day)', max_value=2520, min_value=1, widget=forms.TextInput(attrs={'class': 'form-control'}))
    method = forms.ChoiceField(label='Calculation Method', choices=[('PAR','Parametric'),('HIS','Historical'),('MC','Monte Carlo')], widget=forms.Select(attrs={'class': 'form-control'}))
    plotType = forms.ChoiceField(label='Plot Type', choices=[('PV','Portfolio Value'),('VAR','Value at Risk (VaR)'),('ES','Expected Shortfall (ES)')], widget=forms.RadioSelect(attrs={'class': 'form-control radio-sel'}))

class OptionForm(forms.Form):
    ticker = forms.CharField(label='Ticker', widget=forms.TextInput(attrs={'class': 'form-control'}))
    initial = forms.DecimalField(label='Initial Investment', widget=forms.TextInput(attrs={'class': 'form-control'}))
    window = forms.IntegerField(label='Rolling Window Length (Year)', max_value=10, min_value=1, widget=forms.TextInput(attrs={'class': 'form-control'}))
    startDate = forms.DateField(label='Position Date', widget=forms.DateInput(attrs={'class': 'form-control'}))
    endDate = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'class': 'form-control'}))
    varp = forms.DecimalField(label='VaR Probability', max_value=0.9999, min_value=0.0001, decimal_places=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    esp = forms.DecimalField(label='ES Probability', max_value=0.9999, min_value=0.0001, decimal_places=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nday = forms.IntegerField(label='N Day Horizon (Day)', max_value=2520, min_value=1, widget=forms.TextInput(attrs={'class': 'form-control'}))
    method = forms.ChoiceField(label='Calculation Method', choices=[('PAR','Parametric'),('HIS','Historical'),('MC','Monte Carlo')], widget=forms.Select(attrs={'class': 'form-control'}))
    plotType = forms.ChoiceField(label='Plot Type', choices=[('PR','Price'),('VAR','Value at Risk (VaR)'),('ES','Expected Shortfall (ES)')], widget=forms.RadioSelect(attrs={'class': 'form-control radio-sel'}))

