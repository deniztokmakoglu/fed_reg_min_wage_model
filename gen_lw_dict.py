"""
Weighted Average Living Wage
Author: Deniz Tokmakoglu
"""

import json
import pandas as pd

#Mapping Household Types to Familty types
#(Matches Census Data to Living Wage Data) for Worst Case Scenario
UPPER_BOUND = {
    '1-person household': "1 ADULT0 Children",
    '2-person household': "1 ADULT1 Child",
    '3-person household': "1 ADULT2 Children",
    '4-person household': "1 ADULT3 Children",
    "5+ person household": "1 ADULT3 Children"}

#Mapping Household Types to Familty types
#(Matches Census Data to Living Wage Data) for Best Case Scenario
LOWER_BOUND = {
    '1-person household': "1 ADULT0 Children",
    '2-person household': "2 ADULTS0 Children",
    '3-person household': "2 ADULTS1 Child",
    '4-person household': "2 ADULTS2 Children",
    "5+ person household": "2 ADULTS3 Children"}

HH_TYPES = {"1-person household": ["B11016_010E"],
           "2-person household": ["B11016_002E", "B11016_011E"],
           "3-person household": ["B11016_004E", "B11016_012E"],
           "4-person household": ["B11016_005E", "B11016_013E"],
           "5+ person household": ["B11016_006E", "B11016_007E",
                                  "B11016_008E", "B11016_014E",
                                  "B11016_015E", "B11016_016E"]}


def go(filename="clean_data/living_wages_by_county.json"):
    '''
    The main function that reads all the raw data and generates the
    wages for different scenarios for each county.
    Inputs:
        -filename (str): output file name
    Returns:
        -wages_dictionary(nested dictionary): the dictionary that maps each county to the scenarios.
    '''
    try:

        with open("raw_data/county_info.json", "r") as file:
            county_info_dict = json.load(file)

        with open("raw_data/household_sizes.json", "r") as file:
            hh_sizes_dicts = json.load(file)

        living_wage_df = pd.read_csv("raw_data/living_wage_data.csv")

    except Exception as e:

        print("Cannot read the json files in gen_lw_dict.py.")
        print(f"Make sure the raw files are generated. The error is {e}")

    hh_size_data = process_hh_type_county(hh_sizes_dicts, county_info_dict)
    wages_dictionary = compile_wages(living_wage_df, hh_size_data)

    with open(filename, "w") as file:
        json.dump(wages_dictionary, file)

    return wages_dictionary


def process_hh_type_county(hh_sizes_dicts, county_info_dict):
    '''
    Processes the raw data of county level household type.
    Inputs:
        - hh_sizes_dicts(list of dictionaries): household level dictionaries that
                                                comes from Census API.
        - county_info_dict(dictionary): Dictionary that maps county codes to county names
                                        and fips codes for IL.
    Returns:
         -df(pandas dataframe): dataframe containing number of
                                household type information for each county.
    '''
    df = pd.DataFrame(columns = HH_TYPES.keys())
    for county_hh_dict in hh_sizes_dicts:
        perc_per_type = {}
        perc_per_type["County ID"] = county_info_dict[county_hh_dict['county']].values()
        perc_per_type["County"] = county_info_dict[county_hh_dict.pop('county')].keys()
        del county_hh_dict["state"]
        num_hhs = sum(county_hh_dict.values())
        for hh_type, var_lst in HH_TYPES.items():
            num_in_hh_type = 0
            for var in var_lst:
                num_in_hh_type += county_hh_dict[var]
            perc_per_type[hh_type] = [num_in_hh_type / num_hhs]
        county_df = pd.DataFrame.from_dict(perc_per_type)
        df = pd.concat([df,county_df])
    df = df.set_index("County ID")

    return df


def compile_wages(living_wage_df, hh_size_data):
    """
    Creates the best and worst case wage levels for each county and household type in IL.
    Inputs:
        - living_wage_df(pandas dataframe): dataframe that contains
                                            living wage for each county and household type.
        - hh_size_data(pandas dataframe): dataframe that containts
                                          household type frequencies for each county.
    Returns:
           - wage_dict(nested dictionary): dictionary that maps
                                           each conty to best and worst case wages.
    """
    wage_dict = {county:{} for county in living_wage_df["County"].unique()}
    for county in wage_dict:
        county_wage = living_wage_df[living_wage_df["County"] == county]
        county_hhs = hh_size_data[hh_size_data["County"] == county]
        wage_dict[county]["UB LW"] = gen_avg_wages(county_wage, county_hhs, UPPER_BOUND)
        wage_dict[county]["LB LW"] = gen_avg_wages(county_wage, county_hhs, LOWER_BOUND)
    return wage_dict


def gen_avg_wages(county_wage, count_hhs, mapping_dict):
    """
    Generates an average living wage for different types of families.
    Inputs:
        -county_wage (pandas dataframe): county level living wage dataframe.
        -county_hhs(pandas dataframe): county level household type dataframe.
        -mapping_dict(dictionary): maps types of families to be aggregated based on the scenario.
    Returns:
        -avg_wage(flot): the average wage.
    """
    avg_wage = 0
    for census_hh, lw_hh in mapping_dict.items():
        row = county_wage[county_wage["Family Structure"] == lw_hh]
        avg_wage += float(count_hhs[census_hh]) * float(row["Living Wage"])
    return round(avg_wage, 2)


if __name__ == "__main__":
    usage = "python3 gen_lw_dict.py"
    data_filename = "clean_data/living_wages_by_county.json"
    go(data_filename)
