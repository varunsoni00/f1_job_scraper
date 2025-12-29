# Importing the required libraries
import os
import time
import warnings
import requests
import openpyxl
import xlsxwriter
import pandas as pd
from pathlib import Path
from pandas.io.formats import excel
from scrapper import (mclaren, ferrari, mercedes, red_bull_racing, williams,
                      aston_martin, kick_sauber, racing_bulls, hass, alpine, cadillac)


# Calculating the runtime of the code
start_time = time.time()


# Ignoring all the warnings
warnings.filterwarnings("ignore")

# By default, ignoring all the header styling created automatically on converting pandas df into excel
excel.ExcelFormatter.header_style = None


# *********************************************** Formula-1 Definitions ************************************************
# Defining all the teams and current drives in f1
teams = {"Mclaren": ["Lando Norris", "Oscar Piastri"],
         "Ferrari": ["Lewis Hamilton", "Charles Leclerc"],
         "Mercedes": ["George Russel", "Kimi Antonelli"],
         "Red Bull Racing": ["Max Verstrappen", "Yuki Tsunoda"],
         "Williams": ["Carlos Sainz", "Alex Albon"],
         "Aston Martin": ["Fernando Alsonso", "Lance Stroll"],
         "Kick Sauber": ["Nico Hulkenberg", "Gabriel Bortoleto"],
         "Racing Bulls": ["Isack Hadjar", "Liam Lawson"],
         "Hass": ["Esteban Ocon", "Oliver Bearman"],
         "Alpine": ["Pierre Gasly", "Franco Colapinto"],
         "Cadillac": []}

# Defining the link to all the teams career pages
f1_teams_job_portal = {"Mclaren": "https://racingcareers.mclaren.com/",
                       "Ferrari": "https://jobs.ferrari.com/search/?createNewAlert=false&q=&options"
                                  "FacetsDD_country=&optionsFacetsDD_customfield1=",
                       "Mercedes": "https://www.mercedesamgf1.com/careers/vacancies",
                       "Red Bull Racing": "https://www.redbullracing.com/int-en/careers",
                       "Williams": "https://careers.williamsf1.com/jobs",
                       "Aston Martin": "https://www.astonmartinf1.com/en-GB/careers",
                       "Kick Sauber": "https://www.sauber-group.com/corporate/careers",
                       "Racing Bulls": "https://jobs.redbull.com/api/search?pageSize=10&locale=en&country=int",
                       "Hass": "https://haasf1team.bamboohr.com/careers/list",
                       "Alpine": "https://alliancewd.wd3.myworkdayjobs.com/wday/cxs/alliancewd/alpine-racing-careers/"
                                 "jobs",
                       "Cadillac": "https://opportunities.cadillacf1team.com/"}


# We will also define the scrapper function name for each team
scrapper_functions = {"Mclaren": mclaren,
                      "Ferrari": ferrari,
                      "Mercedes": mercedes,
                      "Red Bull Racing": red_bull_racing,
                      "Williams": williams,
                      "Aston Martin": aston_martin,
                      "Kick Sauber": kick_sauber,
                      "Racing Bulls": racing_bulls,
                      "Hass": hass,
                      "Alpine": alpine,
                      "Cadillac": cadillac}

# *********************************************** Formula-1 Definitions ************************************************

# x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x- Start of function definitions -x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x

# **************************************************** pretty_print ****************************************************
# To print each error statement with equal width
def pretty_print(word):
    total_width = 100
    stars_needed = total_width - len(word)
    stars_before = stars_needed // 2
    stars_after = stars_needed - stars_before
    print(f"{'*' * stars_before} {word} {'*' * stars_after}".center(total_width))


# **************************************************** pretty_print ****************************************************

# x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x- End of function definitions -x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x

# ************************************************** Extracting Jobs ***************************************************
# Creating a dict where keys will be team names and values will be list of extracted job information from web
# Later we will take all the df's in this dict and then put it into an excel file with different sheets as team name
f1_jobs = dict()

# Informing the user about the current status of the code
pretty_print("Extracting F1 Jobs")

# Iterating through all the teams and extracting the job information from their respective website using their scrapper
for team, link in f1_teams_job_portal.items():

    # Ignoring the Kick-Sauber team as their website has been taken down
    # This team will convert into Audi in 2026
    if team == "Kick Sauber":
        continue

    # Printing the current team name to let the user know
    print("\nF1 Team:", team)

    # We are working with the json data for the alpine page
    # And their page uses post request not get we also have to add some headers to make it work properly
    # So we will follow a different step is the team is alpine
    if team in ["Alpine"]:
        response = requests.post(link, headers={"Content-Type": "application/json"}, verify=False)

    # The williams f1 page also requires user-agent headers to establish the connection correctly
    # Without which the connection reports in 403 error
    elif team in ["Williams"]:
        response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, verify=False)

    else:
        # We will use the request library to get the html response of the job page
        response = requests.get(link, verify=False)

    
    # After getting the response printing the status code for the current team
    print("Status Code:", response.status_code)

    
    # If the response is received and the connection is successful the html status code will be 200
    # For the sites where we get the expected staus code we will move forward and extract information
    # Rest of them we will skip for now
    if response.status_code == 200:
        # Now we will extract the html code for the current teams job page
        html_code = response.text
        
        # We will take this html code and pass it to the respective scrapper to extract the job information
        # This scrapper will return 2 things the columns for the current team along with list of information
        df_headers, current_team_openings = scrapper_functions[team](html_code)

        # Once we have the information headers and information for the current team we will create its df
        # And append the df into the f1_jobs list
        df = pd.DataFrame(columns=df_headers)

        # Adding the job role information into the df
        for jobs in current_team_openings:
            df.loc[len(df)] = jobs

        if team in ["Racing Bulls"]:
            # For racing bulls we will sort the category columns, so that all the F1 based jobs are at top
            df = df.sort_values(by="Category", key=lambda x: x != "F1")

        # Adding the current team df into the dictionary of df
        f1_jobs[team] = df

# Creating the output excel file
# Get the directory where the current script is located
script_dir = Path(__file__).resolve().parent

# Go one directory up
parent_dir = script_dir.parent

# Define the output directory path
output_dir = parent_dir / "output"

# Create the output directory if it doesn't exist
output_dir.mkdir(exist_ok=True)

# Using os.path.join instead of directly using the path so that in works in cross-platform machines
with pd.ExcelWriter(os.path.join(output_dir, "F1_Jobs.xlsx"), engine="xlsxwriter") as writer:
    
    # Iterating though all the df's and adding them in the output excel
    for team, df in f1_jobs.items():
        df.to_excel(writer, sheet_name=team + "-" + str(len(df)), index=False)
            

# ************************************************** Extracting Jobs ***************************************************


# Calculating the runtime of the code
end_time = time.time()
run_time = end_time - start_time
print("\nRuntime {:6F} seconds".format(run_time))


