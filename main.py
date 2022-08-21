import os
from bs4 import BeautifulSoup
import requests
import plotly.graph_objects as go

def generalStats():
    fbref = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats').text
    soup = BeautifulSoup(fbref, 'html.parser')
    desired_stats = ["passes_pct", "passes_pct_short", "passes_pct_medium", "passes_pct_long", "progressive_pass_pct",
                     "final_third_pass_pct", "possession"]
    extra_stats = ["progressive_passes", "passes_into_final_third", "passes_completed"]
    teams_list = ["arsenal","aston villa","bournemouth","brentford","brighton","chelsea","crystal palace",
                  "everton","fulham","leeds united","leicester city","liverpool","manchester city","manchester utd",
                  "newcastle utd","nott'ham forest","southampton","tottenham","west ham","wolves"]

    team_one = input("Please enter the first team you would like to compare: ").lower() # letting the user enter the teams to compare
    team_two = input("PLease enter the second team you would like to compare: ").lower()

    teams = {k: dict.fromkeys(desired_stats,0) for k in teams_list}
    teams_2 = {k: dict.fromkeys(extra_stats,0) for k in teams_list}

    rows = soup.find_all('tr')   # Collect all rows in the fbref for the Prem 22/23

    for index, row in enumerate(rows):
        team_name = row.find('th').get_text()
        stats = row.find_all('td')

        if team_name.lower() in list(teams.keys()):
            for stat in stats:
                if stat.get('data-stat') in desired_stats:  # add the stat to the dictionary
                    teams[team_name.lower()][stat.get('data-stat')] = float(stat.get_text())
                elif stat.get('data-stat') in extra_stats:  # add the stat to the dictionary
                    teams_2[team_name.lower()][stat.get('data-stat')] = float(stat.get_text())


    for team in teams:
        teams[team.lower()]["progressive_pass_pct"] = (teams_2[team.lower()]["progressive_passes"] / teams_2[team.lower()]["passes_completed"])*1000
        teams[team.lower()]["final_third_pass_pct"] = (teams_2[team.lower()]["progressive_passes"] / teams_2[team.lower()]["passes_completed"])*1000

        if not os.path.exists(f'C:/Users/kbruv/PycharmProjects/scraper/teams/{team.title()}'):
            os.mkdir(f'C:/Users/kbruv/PycharmProjects/scraper/teams/{team.title()}')
        with open(f'teams/{team.title()}/{team}.txt', 'w') as f:
            f.write(f'{team.title()} \n\n')
            for stat in teams[team]:
                f.write(f"{stat}: {teams[team][stat]}\n")
            f.close()


    radar = go.Figure()

    radar.add_trace(go.Scatterpolar(
        r=[*teams[team_one].values()],
        theta=desired_stats,
        fill='toself',
        name=team_one.title()
    ))
    radar.add_trace(go.Scatterpolar(
        r=[*teams[team_two].values()],
        theta=desired_stats,
        fill='toself',
        name=team_two.title()
    ))

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0,100]
            )),
        showlegend=False
    )

    radar.show()
    radar.write_image(f'teams/{team_one.title()}/{team_one} vs {team_two}.jpg', engine='kaleido')
    radar.write_image(f'teams/{team_two.title()}/{team_one} vs {team_two}.jpg', engine='kaleido')


if __name__ == "__main__":
    generalStats()