
import os
import gen_plots

"""
This is an application module that allows a user to generate
county based welfare
"""

WELCOME_MESSAGE = """
******* Wage Model Generator *******
Welcome to the model. 
Currently creating the virtual environment
and installing necessary packages to run the model...
"""

ASPECT_MENU = """
******* Wage Model Generator *******
******* Aspect Menu ****************
Welcome to the wage model generator application.
What aspects of the model do you want to run?

(A) Run everything. [API, Data Scraping, Data Cleaning and Analysis]
(B) Run only analysis using pre-generated, cleaned data from API and Scraping.
(C) Quit the Program

"""

MAP_MENU = """
******* Wage Model Generator *******
******* Map Menu *******************
Please choose which maps you want to generate.

(1) Wage Comparison
(2) Percent Affected by New Wage
(3) Effectiveness of New Wage Relative to Conservative Living Wage
(4) Difference in New Wage and Conservative Living Wage
(5) Difference in New Wage and Generous Living Wage
(6) Unemployment Repercussions
(7) See all maps
(8) Quit
"""

WAGE_INPUT_MENU = """
******* Wage Model Generator *******
Please enter your wage input (integer): 
"""

POSSIBLE_OPTS_MAIN = [1, 2, 3, 4, 5, 6, 7, 8]
POSSIBLE_OPTS_ASPECT = ["A", "B", "C"]

def get_map_info():
    """
    Gets the user input for displaying the maps.
    """
    option = -1
    while True:
        print(MAP_MENU)
        option = int(input("Please enter your choice: "))
        if option not in POSSIBLE_OPTS_MAIN:
            print(f"Please enter a valid option. {option} is not valid.")
        elif option == 8:
            print("Exiting the program...")
            return option
        else:
            print(f"Your option for generating the map is {option}")
            return option


def get_aspect_info():
    """
    Gets the aspect information to determine to
    what extend the user wants to run the code.
    """
    aspect = ""
    while True:
        print(ASPECT_MENU)
        aspect = str(input("Please enter your choice: "))
        if aspect not in POSSIBLE_OPTS_ASPECT:
            print(f"Please enter a valid option. {aspect} is not valid.")
        elif aspect == "C":
            print("Exiting the program")
            return aspect
        else:
            print(f"Your option for model aspect is {aspect}")
            return aspect

def get_user_wage():
    """
    Gets the user wage input
    """
    print(WAGE_INPUT_MENU)
    wage_input = int(input("Wage Input: "))
    return wage_input

def generate_agg_data(wage_input):
    """
    Function that calls the python file to generate
    the aggregate data with the user wage input.
    """
    print(f"Updating minimum wage to {wage_input}...")
    os.system(f"python3 gen_agg_data.py {wage_input} {0}")


def generate_raw_clean_data(aspect_choice, wage_input):
    """
    Function that calls the necessary python
    files to generate raw and clean data.
    """
    assert aspect_choice == "A", "The user did not choose to run everything."
    print("Pulling Census API...")
    os.system("python3 census_api.py")
    print("Scraping MIT Living Wage Data...")
    os.system("python3 lw_crawler.py")
    print("Generating household level income data...")
    os.system("python3 gen_hh_level_data.py")
    print("Generating weighted living wages for counties...")
    os.system("python3 gen_lw_dict.py")
    print("Generating master data set...")
    os.system(f"python3 gen_agg_data.py {wage_input} {True}")


def generate_visuals():
    """
    Function that calls the python
    file to generate visuals.
    """
    print("Generating visual(s)...")
    visuals = gen_plots._go("clean_data/master_data.csv")
    return visuals

def main():
    """
    The main function that runs the application.
    """
    print(WELCOME_MESSAGE)
    ###### Getting the user input#######
    aspect_choice = get_aspect_info()
    if aspect_choice == "C":
        print("Exited")
        return None
    wage_input = get_user_wage()
    ######### Aspect Choice ############
    #generates everything from beginning
    if aspect_choice == "A":
        generate_raw_clean_data(aspect_choice, wage_input)
    else:
        generate_agg_data(wage_input)
    while True:
        model_choice = get_map_info()
        if model_choice == 8:
            print("Thank you for running our model.")
            print("Exited")
            return None
        print("Thank you, we are working on it now.")
        p1, p2, p3, p4, p5, p6 = generate_visuals()
        print("Completed! Now you can take a look at the map(s)!")
        if model_choice == 1:
            p1.show()
        elif model_choice == 2:
            p2.show()
        elif model_choice == 3:
            p3.show()
        elif model_choice == 4:
            p4.show()
        elif model_choice == 5:
            p5.show()
        elif model_choice == 6:
            p6.show()
        elif model_choice == 7:
            p1.show()
            p2.show()
            p3.show()
            p4.show()
            p5.show()
            p6.show()

if __name__ == "__main__":
    # This is the entry point into the application
    usage = "python3 run_wage_model.py"
    main()
