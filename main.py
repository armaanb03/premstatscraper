import os
from bs4 import BeautifulSoup
import requests
import plotly.graph_objects as go


def generalstats():
    fbref = requests.get('https://fbref.com/en/comps/9/Premier-League-Stats').text
    soup = BeautifulSoup(fbref, 'html.parser')
    desired_stats = ["passes_pct", "passes_pct_short", "passes_pct_medium", "passes_pct_long", "progressive_pass_pct",
                     "final_third_pass_pct", "possession"]
    extra_stats = ["progressive_passes", "passes_into_final_third", "passes_completed"]
    teams_list = ["arsenal", "aston villa", "bournemouth", "brentford", "brighton", "chelsea", "crystal palace",
                  "everton", "fulham", "leeds united", "leicester city", "liverpool", "manchester city",
                  "manchester utd", "newcastle utd", "nott'ham forest", "southampton", "tottenham", "west ham", "wolves"]
    names_and_alternates = {"forest": "nott'ham forest", "nottingham forest": "nott'ham forest", "spurs": "tottenham",
                            "tottenham hotspur": "tottenham", "leicester": "leicester city", "newcastle": "newcastle utd",
                            "newcastle united": "newcastle utd", "leeds": "leeds united", "leeds utd": "leeds united",
                            "manchester united": "manchester utd", "city": "manchester city", "west ham united": "west ham"}
    # dictionaries and lists for the required stats, extra stats used in calculation, list of teams, and synonym names

    team_one = input("Please enter the first team you would like to compare: ").lower()  # letting the user enter the teams to compare
    team_two = input("PLease enter the second team you would like to compare: ").lower()

    if team_one in names_and_alternates.keys():     # converting the input team names into the fbref version if they are an alternate name
        team_one = names_and_alternates[team_one]
    if team_two in names_and_alternates.keys():
        team_two = names_and_alternates[team_two]

    user_team_list = sorted([team_one, team_two])

    teams_and_stats_dict = {k: dict.fromkeys(desired_stats, 0) for k in teams_list}
    teams_and_extra_stats_dict = {k: dict.fromkeys(extra_stats, 0) for k in teams_list}
    # generating two nested dicts to hold teams, and for each team a dict with stat names and values

    rows = soup.find_all('tr')   # Collect all rows in the fbref for the Prem 22/23

    for row in rows:  # looping through every row containing teams and stats
        team_name = row.find('th').get_text()
        stats = row.find_all('td')

        if team_name.lower() in list(teams_and_stats_dict.keys()):
            for stat in stats:
                if stat.get('data-stat') in desired_stats:  # add the stat to the dictionary
                    teams_and_stats_dict[team_name.lower()][stat.get('data-stat')] = float(stat.get_text())
                elif stat.get('data-stat') in extra_stats:  # add the stat to the dictionary
                    teams_and_extra_stats_dict[team_name.lower()][stat.get('data-stat')] = float(stat.get_text())

    visual_coefficient = 500

    for team in teams_and_stats_dict:
        teams_and_stats_dict[team.lower()]["progressive_pass_pct"] = \
            (teams_and_extra_stats_dict[team.lower()]["progressive_passes"] / teams_and_extra_stats_dict[team.lower()]["passes_completed"]) * visual_coefficient
        teams_and_stats_dict[team.lower()]["final_third_pass_pct"] = \
            (teams_and_extra_stats_dict[team.lower()]["progressive_passes"] / teams_and_extra_stats_dict[team.lower()]["passes_completed"]) * visual_coefficient

        if not os.path.exists(f'C:/Users/kbruv/PycharmProjects/scraper/teams/{team.title()}'):
            os.mkdir(f'C:/Users/kbruv/PycharmProjects/scraper/teams/{team.title()}')
        with open(f'teams/{team.title()}/{team}.txt', 'w') as f:
            f.write(f'{team.title()} \n\n')
            for stat in teams_and_stats_dict[team]:
                if stat == "progressive_pass_pct" or stat == "final_third_pass_pct":
                    f.write(f"{stat}: {teams_and_stats_dict[team][stat] / 5:.2f}%\n")
                else:
                    f.write(f"{stat}: {teams_and_stats_dict[team][stat]:.2f}%\n")
            f.close()

    radar = go.Figure()

    radar.add_trace(go.Scatterpolar(
        r=[*teams_and_stats_dict[team_one].values()],
        theta=desired_stats,
        fill='toself',
        name=team_one.title()
    ))
    radar.add_trace(go.Scatterpolar(
        r=[*teams_and_stats_dict[team_two].values()],
        theta=desired_stats,
        fill='toself',
        name=team_two.title()
    ))

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False
    )

    radar.update_layout(showlegend=True)

    # writing the graph to a jpg and html file in each team's individual folder
    radar.write_image(f'teams/{team_one.title()}/{user_team_list[0]} vs {user_team_list[1]}.jpg', engine='kaleido')
    radar.write_image(f'teams/{team_two.title()}/{user_team_list[0]} vs {user_team_list[1]}.jpg', engine='kaleido')


if __name__ == "__main__":
    print("Welcome to the Premier League stat comparison, some stats in the radar plot have values altered for visual effect")
    generalstats()
