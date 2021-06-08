"""
Create HH level income data
Author: Caton Brewster
"""

import json
import pandas as pd
import numpy as np


INCOME_BIN_VARS = {"Less than 10K" : "DP03_0052E",
                     "10K - 14.9K" : "DP03_0053E",
                     "15K - 24.9K" : "DP03_0054E",
                     "25K - 34.9K" : "DP03_0055E",
                     "35K - 49.9K" : "DP03_0056E",
                     "50K - 74.9K" : "DP03_0057E",
                     "75K - 99.9K" : "DP03_0058E",
                     "100K - 149.9K" : "DP03_0059E",
                     "150K - 199.9K" : "DP03_0060E",
                     "200K +" : "DP03_0061E"}

INCOME_BINS = INCOME_BIN_VARS.keys()


def go(filename="clean_data/hh_level_data.csv"):
    '''
    The main function to generate the hh_level data.
    Inputs:
        -filename: the output filename
    Returns:
        -hh_level_data(dataframe)
    '''
    with open("raw_data/income_buckets.json", "r") as file:
        county_income_info = json.load(file)

    with open("raw_data/county_info.json", "r") as file:
        county_id_info = json.load(file)

    c_df = process_income_data(county_income_info, county_id_info)
    hh_level_data = gen_hh_data(c_df)

    hh_level_data.to_csv(filename, index = False)

    return hh_level_data


def process_income_data(county_income_info, county_id_info):
    '''
    Takes a list dictionaries that maps each income bucket to the
    number of people in a county in that income bracket,
    and a dictionary mapping county codes
    to county names, and returns a dataframe with one row
    per income bucket per county
    inputs:
        - county_income_info: list of dictionaries
        - county_id_info: dictionary mapping county codes to names
    output: dataframe
    '''
    df = pd.DataFrame()
    for county_dct in county_income_info:
        county_df = convert_dict_to_df(county_dct, county_id_info)
        df = pd.concat([df, county_df])
    return df.reset_index(drop=True)


def convert_dict_to_df(county_dct, county_id_info):
    '''
    For a given dictionary associated with a county, builds a dataframe
    which gives the number of people in each income bracket for the county
    inputs:
        - county_dct: dictionary
        - county_id_info: dictionary mapping county code to county name
    output: dataframe
    '''
    df = pd.DataFrame(INCOME_BINS, columns=["Bins"])
    county_id = county_dct['county']
    county_name_list = list(county_id_info[county_id].keys()) #ugly
    county_name = county_name_list[0] #ugly
    df["County"] = county_name
    df["FIP"]  = county_id_info[county_id][county_name]
    df["Num HHs in Bin"] = [county_dct[INCOME_BIN_VARS[label]] for label in df["Bins"]]
    df["County Size"] = county_dct['DP03_0051E']
    return df


def gen_hh_data(c_df):
    '''
    Takes a dataframe with one county per row and generates
    predicted HH-level data based on the income buckets in each county
    Inputs:
        - c_df (data frame with income bracket info for each county)
    Outputs:
        - DataFrame with one row per HH in Illinois
    '''

    lbs = [5200.00, 10000.00, 15000.00, 25000.00, 35000.00,
            50000.00, 75000.00, 100000.00, 150000.00]
    lb_dict = dict(zip(INCOME_BINS,lbs))
    ubs = [9999.99, 14999.99, 24999.99, 34999.99, 49999.99,
            74999.99, 99999.99, 149999.99, 199999.99]
    ub_dict = dict(zip(INCOME_BINS,ubs))

    #create bounds + increment
    c_df["lb"] = c_df.apply(lambda row: lb_dict.get(row["Bins"], 0), axis=1)
    c_df["ub"] = c_df.apply(lambda row: ub_dict.get(row["Bins"], 0), axis=1)
    c_df["increment"] = (c_df["ub"] - c_df["lb"]) / c_df["Num HHs in Bin"]

    # remove those above 200K - we don't know their salary
    c_df = c_df[c_df["Bins"] != "200K +"]
    #expand data - 1 row per HH

    df = pd.DataFrame({col:np.repeat(c_df[col].values, c_df['Num HHs in Bin'], axis=0)
                        for col in c_df})
    del df["Num HHs in Bin"]

    #created Predicted Salary as cum sum of increment
    df["cum increment"]  = df.groupby(['County','Bins'])['increment'].cumsum()
    df["Predicted Salary"] = df["lb"] + df["cum increment"]
    df["Predicted Salary"] = df["Predicted Salary"].round(2)
    df["Hourly Wage"] = df["Predicted Salary"] / 2080
    df.loc[(df["Hourly Wage"] < 10), 'Hourly Wage'] = 10
    df["Hourly Wage"] = df["Hourly Wage"].round(2)
    df["Hours"] = 40.00
    df.loc[df["Predicted Salary"] < 20800, 'Hours'] = \
        df["Predicted Salary"] / (df["Hourly Wage"] * 52)
    df["Hours"] = df["Hours"].round(2)

    #clean up rounding errors in Predicted Salary relation to Hourly Wage and Hours
    df["Predicted Salary"] = df["Hourly Wage"] * df["Hours"] * 52

    return df.loc[:, df.columns.intersection(\
            ['County','County Size', 'FIP', 'Bins', 'Hours', 'Predicted Salary', 'Hourly Wage'])]
