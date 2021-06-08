"""
Generate variables related to input wage and living wage and then
aggregate to create master dataset

Author: Caton Brewster
"""

import json
import pandas as pd
import numpy as np
import sys

def go(new_wage=15, full_gen=False, filename="clean_data/master_data.csv"):
    '''
    Run all functions needed to create a master aggregated wage dataset
    based on Census data and MIT Living Wage Caculator

    Inputs:
        - new_wage (int): proposed new federal minimum wage
        - full_gen (boolean): whether to regenerate all underyling data
        - filename (string): filename to save dataset to
    Outputs:
        - (DataFrame): aggregated dataset
    '''

    if full_gen:
        # regenerate underlying data
        with open("clean_data/living_wages_by_county.json", "r") as file:
            living_wage_dict = json.load(file)

        hh_df = pd.read_csv("clean_data/hh_level_data.csv")
        hh_df["index"] = hh_df.index
        hh_df = hh_df.rename(columns={"Predicted Salary":'Current Agg Income'})

        hh_lw_df = create_lw_vars(hh_df, living_wage_dict)
        hh_lw_df.to_csv("clean_data/hh_level_data_w_lw.csv", index = True)
    else:
        try:
            hh_lw_df = pd.read_csv("clean_data/hh_level_data_w_lw.csv")
        except:
            print("hh_level_data_w_lw.csv doesn't exist yet")
            print("run go() function with full_gen=True to generate")

    hh_nw_lw_df = create_new_wage_vars(hh_lw_df, new_wage)
    agg_df = agg_data(hh_nw_lw_df)
    agg_df_w_vars = gen_new_vars(agg_df)

    agg_df_w_vars.to_csv(filename, index = False)

    return agg_df_w_vars


def create_lw_vars(hh_df, living_wage_dict):
    '''
    Generates hh-level variables related to the lower bound and
    upper bound living wage

    Inputs:
        - hh_df: (Dataframe) hh-level income data
        - living_wage_dict: (Dictionary) dictionary mapping county to
                            living wages in each county
    '''
    for bound in ["UB LW", "LB LW"]:

        hh_df["County " + bound] = hh_df.apply(lambda row:
                                        living_wage_dict[row["County"]][bound],
                                        axis=1)

        hh_df["% Affected by " + bound] = (hh_df["Hourly Wage"] <
                                        hh_df["County " + bound])

        hh_df[bound + " Wage"] = hh_df.apply(lambda row:
                                    living_wage_dict[row["County"]][bound]
                                    if row["Hourly Wage"] <=
                                    living_wage_dict[row["County"]][bound]
                                    else row["Hourly Wage"], axis=1)

        #choose random subset based on the unemployment model to lose job
        hh_df[bound + " # Unemp. by County"] = hh_df.apply(lambda row:
                                               int(((row[bound + " Wage"] *
                                               0.26579 - 2.74474)/155.76) *
                                               row["County Size"]), axis=1)

        hh_df.loc[hh_df.groupby('County').apply(
                                            lambda x:
                                            x[x["Hourly Wage"] <=
                                            x["County " + bound]].sample(int(
                                            x[x["Hourly Wage"] <=
                                            x["County " + bound]]
                                            [bound + " # Unemp. by County"].mean()),
                                            random_state=1))["index"],
                                            bound + " Wage"] = 0

        hh_df[bound + " Agg Income"] = (hh_df[bound + " Wage"] *
                                        hh_df["Hours"] * 52.14)
        hh_df["Unemployed at " + bound] = hh_df[bound + " Wage"] == 0

    return hh_df


def create_new_wage_vars(hh_lw_df, new_wage):
    '''
    Generate hh-level variables related to the user-inputted wage

    Inputs:
        - hh_lw_df (DataFrame): hh-level income data with living wage vars
        - new_wage (int): user-inputted minimum wage
    '''

    #CBO model of unemployment
    unemp_model = (new_wage * 0.26579 - 2.74474)/155.76

    hh_lw_df["Entered Wage"] = new_wage
    hh_lw_df["% Affected by New Wage"] = (hh_lw_df["Hourly Wage"] <
                                        hh_lw_df["Entered Wage"])
    hh_lw_df["New Wage"] = np.where(hh_lw_df["Hourly Wage"] <= new_wage,
                                    new_wage, hh_lw_df["Hourly Wage"])

    #choose random subset to lose job, with same rate applied to each county
    hh_lw_df.loc[hh_lw_df.groupby('County').apply(
                                            lambda x:
                                            x[x["Hourly Wage"] <=
                                            new_wage].sample(
                                            int(unemp_model*len(x)),
                                            random_state=1))["index"],
                                            "New Wage"] = 0

    hh_lw_df["New Wage Agg Income"] = (hh_lw_df["New Wage"] *
                                       hh_lw_df["Hours"] * 52.14)
    hh_lw_df["Unemployed at New Wage"] = hh_lw_df["New Wage"] == 0
    hh_lw_df["% Below LB Living Wage at Inputted Min. Wage"] = (hh_lw_df["New Wage"] <=
                                           hh_lw_df["County LB LW"])
    hh_lw_df["% Below UB Living Wage at Inputted Min. Wage"] = (hh_lw_df["New Wage"] <=
                                           hh_lw_df["County UB LW"])

    return hh_lw_df


def agg_data(hh_nw_lw_df):
    '''
    Aggregates hh-level data into county-level data with outcomes of interest

    Input:
        - hh_new_lw_df (DataFrame): hh-level income data with inputted and
                                    living wage vars
    '''
    agg_df = hh_nw_lw_df.groupby(
             ['County']).agg({"County": 'first',
                                "FIP": 'first',
                                "County Size": 'first',
                                "Entered Wage": 'first',
                                "County UB LW": 'first',
                                "County LB LW": 'first',
                                'Current Agg Income':'sum',
                                'New Wage Agg Income':'sum',
                                'UB LW Agg Income':'sum',
                                'LB LW Agg Income':'sum',
                                "% Below LB Living Wage at Inputted Min. Wage": 'mean',
                                "% Below UB Living Wage at Inputted Min. Wage": 'mean',
                                "% Affected by New Wage": 'mean',
                                "% Affected by UB LW": 'mean',
                                "% Affected by LB LW": 'mean',
                                "Unemployed at New Wage": 'mean',
                                "Unemployed at UB LW": 'mean',
                                "Unemployed at LB LW": 'mean'})
    return agg_df


def gen_new_vars(agg_df):
    '''
    Takes the aggregated county-level DataFrame and creates any
    additional outcomes of interest

    Input:
        - agg_df (DataFrame): county-level aggregated data
    '''

    agg_df["Cost UB LW v New Wage"] = (agg_df['UB LW Agg Income'] -
                                      agg_df['New Wage Agg Income'])
    agg_df["Cost LB LW v New Wage"] = (agg_df['LB LW Agg Income'] -
                                      agg_df['New Wage Agg Income'])

    agg_df["Diff. in LB Living Wage and Entered Wage"] = (agg_df["County LB LW"] -
                                             agg_df["Entered Wage"])
    agg_df["Diff. in UB Living Wage and Entered Wage"] = (agg_df["County UB LW"] -
                                            agg_df["Entered Wage"])


    return agg_df


if __name__ == "__main__":
    usage = "python3 gen_agg_data.py"
    new_wage = int(sys.argv[1])
    full_gen = bool(int(sys.argv[2]))
    go(new_wage, full_gen)