
"""Prep Census Data using API Author: Deniz Tokmakoglu"""

import json
from census import Census
from us import states


def go(filename1 = "raw_data/income_buckets.json",
       filename2 = "raw_data/household_sizes.json",
       filename3 = "raw_data/county_info.json"):
    """
    Main function to get the Census API files.
    Input:
        filename1, 2, 3: filenames to save the raw data.
    Returns:
        Nothing. Saves the Files.
    """
    # census object
    #the key was provided to us by the census bureau.
    census_key = "68e0462c9f5c02a99a7a7bb477fa1ff3d83bedd2"
    c = Census(census_key, year = 2019)
    # list of dictionaries, one per county in IL
    county_codes_unprocessed = c.acs5dp.state_county('NAME', states.IL.fips, '*')
    # lists of dictionaries
    income_status = c.acs5dp.state_county(("DP03_0051E", "DP03_0052E", "DP03_0053E", "DP03_0054E",
                                            "DP03_0055E", "DP03_0056E", "DP03_0057E", "DP03_0058E",
                                            "DP03_0059E", "DP03_0060E", "DP03_0061E"),
                                            states.IL.fips, '*', year = 2019)
    household_sizes = c.acs5.state_county(("B11016_002E", "B11016_004E", "B11016_005E",
                                            "B11016_006E", "B11016_007E", "B11016_008E",
                                            "B11016_010E", "B11016_011E", "B11016_012E",
                                            "B11016_013E", "B11016_014E", "B11016_015E",
                                           "B11016_016E"), states.IL.fips, '*', year = 2019)

    county_info = process_county_codes(county_codes_unprocessed)
    
    #saving files
    with open(filename1, "w") as file1:
        json.dump(income_status, file1)
    with open(filename2, "w") as file2:
        json.dump(household_sizes, file2)
    with open(filename3, "w") as file3:
        json.dump(county_info, file3)

def process_county_codes(lst):
    '''
    Takes list of dictionaries which include the county codes from
    the Census data and builds a dictionary which maps county code to
    county name

    input: lst (list of dictionaries)
    output: dictionary mapping county code to county name
    '''
    county_codes = {}
    for dct in lst:
        state = dct["state"]
        county_name = dct["NAME"].split(",")[0]
        county_code = dct["county"]
        fips_code = state + county_code
        county_codes[county_code] = {county_name : fips_code}
    return county_codes

if __name__ == "__main__":
    usage = "python3 census_api.py"
    go()
