Spot VIPs in your userbase and beta list. 
=========================================

## 1. Get a list of emails

Save it to a file, eg `emails.csv`.

## 2. Pull reportive data 

`cat emails.csv | python3 rapportive.py -o userdata.csv`

This pings Rapportive for each email owners's name, company and title, as well as social profiles. (Currently AngelList, LinkedIn and Twitter)

## 3. Pull follower counts to spot whales

`coffee followers.coffee`

Adds the number of followers each user has on each network, so you can spot whales. 
