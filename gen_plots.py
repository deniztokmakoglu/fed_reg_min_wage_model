"""Create data vizualizations"""
'''Author: Jacob Jameson'''


import plotly
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import sys


def gen_visuals(df_master, counties):
    '''
    Creates plotly objects representing the graphs and maps that the user
    will select.
    Inputs:
        Link(str): the link that contains county level data.
    Returns:
        df(pandas dataframe): dataframe for county level wage data.
    '''

    below_lb_lw_at_new = px.choropleth(df_master, geojson=counties,
        locations='FIP', color='% Below LB Living Wage at Inputted Min. Wage',
        color_continuous_scale="Tealgrn",
        range_color=(
            np.min(df_master['% Below LB Living Wage at Inputted Min. Wage']),
            np.max(df_master['% Below LB Living Wage at Inputted Min. Wage'])),
        scope="usa",
        hover_name='County',
        labels={
            '% Below LB Living Wage at Inputted Min. Wage':
            '% Below LB Living Wage at Inputted Min. Wage'})
    below_lb_lw_at_new.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    below_lb_lw_at_new.update_geos(fitbounds="locations", visible=False)
    below_lb_lw_at_new.update_layout(
        title_text='<br>Effectiveness of New Wage Relative to Conservative ' +
                    'Living Wage<br>(Percentage of Working Houeholds ' +
                    'Below the Lower Bound Living Wage Given Minimum Wage ' +
                    'of $' + str(df_master['Entered Wage'][0]) +')')

    effected_by_new_wage = px.choropleth(df_master, geojson=counties,
        locations='FIP',
        color='% Affected by New Wage',
        color_continuous_scale="Sunsetdark",
        range_color=(
            np.min(
                df_master['% Affected by New Wage']),
            np.max(
                df_master['% Affected by New Wage'])),
        scope="usa",
        hover_name='County',
        labels={
            '% Affected by New Wage': '% Affected by New Wage'})
    effected_by_new_wage.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    effected_by_new_wage.update_geos(fitbounds="locations", visible=False)
    effected_by_new_wage.update_layout(
        title_text='<br>Percentage of Working Households Affected ' +
                    'by the User Inputted Wage of $' + 
                    str(df_master['Entered Wage'][0]))

    wage_comparison = go.Figure()
    wage_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=[10] * 102,
        name='Current Minimum Wage',
        marker_color='indianred'
    ))
    wage_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=df_master['Entered Wage'],
        name='Wage User Entered',
        marker_color='lightsalmon'
    ))
    wage_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=df_master['County UB LW'],
        name='County Upper Bound Living Wage',
        marker_color='blue'
    ))
    wage_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=df_master['County LB LW'],
        name='County Lower Bound Living Wage',
        marker_color='green'
    ))
    wage_comparison.update_layout(title_text='<br>Wage Comparisons')
    wage_comparison.update_layout(barmode='group', xaxis_tickangle=-45)

    unem_comparison = go.Figure()
    unem_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=df_master['Unemployed at LB LW'],
        name='Unemployed at Conservative Estimate of Living Wage',
        marker_color='red'
    ))
    unem_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=df_master['Unemployed at UB LW'],
        name='Unemployed at Generous Estimate of Living Wage',
        marker_color='blue'
    ))
    unem_comparison.add_trace(go.Bar(
        x=df_master['County'],
        y=df_master['Unemployed at New Wage'],
        name='Unemployed at User Inputted Wage of $' + 
             str(df_master['Entered Wage'][0]),
        marker_color='green'
    ))
    unem_comparison.update_layout(
        title_text='<br>Unemployment Repercussions<br>(Percentage ' + 
                    'Point Change in Unemployment Relative to 2019)')
    unem_comparison.update_layout(barmode='group', xaxis_tickangle=-45)

    lb_lw_from_EW = px.choropleth(
        df_master,
        geojson=counties,
        locations='FIP',
        color='Diff. in LB Living Wage and Entered Wage',
        color_continuous_scale="Plasma",
        range_color=(
            np.min(df_master['County LB LW'] - df_master['Entered Wage']),
            np.max(df_master['County UB LW'] - df_master['Entered Wage'])),
        scope="usa",
        hover_name='County',
        labels={
            'Diff. in LB Living Wage and Entered Wage': 
            'Diff. in LB Living Wage and Entered Wage'})
    lb_lw_from_EW.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    lb_lw_from_EW.update_geos(fitbounds="locations", visible=False)
    lb_lw_from_EW.update_layout(
        title_text='<br>Difference Between Conservative ' +
                    'Living Wage and User Inputted Wage of $' +
                    str(df_master['Entered Wage'][0]) + ' (USD)')

    ub_lw_from_EW = px.choropleth(
        df_master,
        geojson=counties,
        locations='FIP',
        color='Diff. in UB Living Wage and Entered Wage',
        color_continuous_scale="Plasma",
        range_color=(
            np.min(df_master['County LB LW'] - df_master['Entered Wage']),
            np.max(df_master['County UB LW'] - df_master['Entered Wage'])),
        scope="usa",
        hover_name='County',
        labels={
            'Diff. in UB Living Wage and Entered Wage':
            'Diff. in UB Living Wage and Entered Wage'})
    ub_lw_from_EW.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    ub_lw_from_EW.update_geos(fitbounds="locations", visible=False)
    ub_lw_from_EW.update_layout(
        title_text='<br>Difference Between Generous ' +
                    'Living Wage and Use Inputted Wage of $' +
                    str(df_master['Entered Wage'][0]) + ' (USD')

    return (wage_comparison, effected_by_new_wage, below_lb_lw_at_new,
             lb_lw_from_EW, ub_lw_from_EW, unem_comparison)


def _go(file_name='clean_data/master_data.csv'):

    with urlopen('https://raw.githubusercontent.com/plotly/' + 
                'datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    df_master = pd.read_csv(file_name)
    return gen_visuals(df_master, counties)
