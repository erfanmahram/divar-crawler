# Divar Crawler
A crawler to get divar's commercial for villa rent and add the data to sqlite database

There are 2 script to get advertises and 2 scripts to get each advertise's info.
get_ads_iran.py and get_info_iran.py are scripts for rent temporary suite apartment in whole Iran, and get_ads_villa.py and get_info_villa.py are scripts for rent temporary villa in whole Iran.

## How to run
First run modles.py to create Models and DB then run each of get_ads scripts to get advertises and save them on db.
After the script finished, you should run the get_info to get information about each advertise.
Notice that you should sign in to divar and get token to access the phone numbers of advertrises.
