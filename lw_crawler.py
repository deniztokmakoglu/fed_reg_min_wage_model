'''
Crawler Engine for Living Wage Data in MIT Website Author: Jacob Jameson
Uses Dr. Lamont Samuel's utility code for webpage crawling
'''

import re
import bs4
import pandas as pd
import util

TYPE_CLASSIFICATIONS = {"living_wage": "odd results",
                        "poverty_wage" : "even",
                        "minimum_wage": "odd"}


def go(data_filename):
    """
    Final function to run everything.
    Inputs:
        data_filename(str): File name for exporting the dataframe.
    Returns:
        Nothing. Exports the data to a csv file.
    """

    starting_url = ("https://livingwage.mit.edu/states/17/locations")
    limiting_domain = "livingwage.mit.edu"
    soup = get_soup(starting_url)
    links = get_links(soup, starting_url, limiting_domain)
    df = create_full_dataframe(links)
    replace = {"Clair County" : "St. Clair County",
    "Island County": "Rock Island County",
    "Daviess County": "Jo Daviess County",
    "Witt County": "De Witt County",
    "Salle County": "LaSalle County"}
    df["County"] = df["County"].replace(replace)
    df.to_csv(data_filename, index = False)


def clean_url(url2, url1 = None):
    """
    This function gets a url, returns the final url
    that can be processed.
    Inputs:
        url1 (set to None for Default): the directing url
        url2: current url
    Returns:
        cleaned url
    """
    url2 = util.remove_fragment(url2)
    if util.is_absolute_url(url2):
        return url2
    return util.convert_if_relative_url(url1, url2)


def get_links(soup, url, limiting_domain):
    """
    This function gets all the urls, in a webpage
    Inputs:
        soup (bs4 object): the soup object for the url
        url: the url
        limiting domain: the limiting domain
    Returns:
        urls(list): list of urls
    """
    final_links = []
    tags_a = soup.find_all("a")
    try:
        for tag in tags_a:
            link = clean_url(tag['href'], url)
            if link is not None:
                if util.is_url_ok_to_follow(link, limiting_domain) and "counties" in link:
                    final_links.append(link)
        return final_links
    except:
        return []


def get_soup(link):
    """
    Gets the soup object from a link.
    Inputs:
        link(str): the link
    Returns:
        soup(bs4 object): the associated soup object
    """
    request = util.get_request(link)
    if request is not None:
        html = util.read_request(request)
        if html is not None:
            soup = bs4.BeautifulSoup(html, "html.parser")
    return soup


def get_titles_adult(table):
    """
    Gets the household types by number of adults.
    Inputs:
        table(bs4 object): html tag that contains the table in the link.
    Returns:
        rv(list): the adult types.
    """
    adults = str(table.find('tr')).split("\n")[2:5]
    rv = []
    for i in adults:
        adult = re.findall(r"\d\s\w*", i)
        if len(adult) > 1:
            adult = adult[0] + " " + adult[1]
            rv.append(adult)
        else:
            rv.append(adult[0])
    return rv


def get_titles_children(table):
    """
    Gets the household types by number of children.
    Inputs:
        table(bs4 object): html tag that contains the table in the link.
    Returns:
        rv(list): types of families by children.
    """
    children = str(table.find_all('tr')[1]).split("\n")[2:6]
    rv = []
    for i in children:
        child = re.findall(r"(\d)\xa0(\w*)", i)[0]
        rv.append(child[0] + ' ' + child[1])
    return rv


def get_values(table, classification):
    """
    Gets the living wage values by household type.
    Inputs:
        table(bs4 object): html tag that contains the table in the link.
        classifications (dictionary): classifications for the different wage types.
    Returns:
        values(list): the wage values.
    """
    class_val = TYPE_CLASSIFICATIONS[classification]
    if class_val == "odd":
        value_str = str(table.find_all("tr", class_=class_val)[1].find_all('td')[1:])
    else:
        value_str = str(table.find("tr", class_=class_val).find_all('td')[1:])
    values = re.findall(r"\d+.\d+", value_str)
    return values


def scrape_county_level_data(link):
    """
    Helper function for create_single_dataframe
    Scrapes the link for county level wage classifications data.
    Inputs:
        link(str): the link to be scraped
    Returns:
        rv(list): county level information
    """
    soup = get_soup(link)
    title = str(soup.find('title'))
    county = re.findall(r"\w*\sCounty", title)
    rv = [county]
    if "County, Illinois" in str(title): #check if it is a county level Illinois data page
        table = soup.find('table', class_ = "results_table table-striped")
        adults = get_titles_adult(table)
        children = get_titles_children(table)
        living_wage = get_values(table, "living_wage")
        poverty_wage = get_values(table, "poverty_wage")
        minimum_wage = get_values(table, "minimum_wage")
        index = 0
        for adult in adults:
            for child in children:
                row = []
                row.append(adult + child)
                row.append(float(living_wage[index]))
                row.append(float(poverty_wage[index]))
                row.append(float(minimum_wage[index]))
                rv.append(row)
                index += 1
    return rv


def create_single_dataframe(link):
    """
    Creates a single data frame for a county level data.
    Inputs:
        Link(str): the link that contains county level data.
    Returns:
        df(pandas dataframe): dataframe for county level wage data.
    """

    data = []
    county_data = scrape_county_level_data(link)
    for value in county_data[1:]:
        row = [county_data[0][0], value[0], value[1], value[2], value[3]]
        data.append(row)
    df = pd.DataFrame(data, columns = ['County', 'Family Structure',
                        'Living Wage','Poverty Wage','Minimum Wage'])
    return df


def create_full_dataframe(links):
    """
    Creates the full dataframe with different counties.
    Inputs
        Links(lst): list of all the county level data links to be scraped.
    Returns
        df(pandas dataframe): Data Frame that contains all the wage data for Illinois Counties.
    """

    frames = []
    for link in links:
        frames.append(create_single_dataframe(link))
    df = pd.concat(frames)
    return df


if __name__ == "__main__":
    usage = "python3 lw_crawler.py"
    DATA_FILENAME = "raw_data/living_wage_data.csv"
    go(DATA_FILENAME)
