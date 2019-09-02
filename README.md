# OWLGlicko

Generates Glicko ratings for all Overwatch League teams in each map-type. Pulls from api.overwatchleague.com for match history.

usage: OWLGlicko.py [-h] [-u] [--random] [--score] [-c] [-t] [-p PERIOD]
                    [-r RATING] [-d DEV] [-v VOL]

optional arguments:
  -h, --help            show this help message and exit
  -u, --update          Update match data from api.overwatchleague.com
  --random              Randomize game order before rating. Use this to
                        mitigate recency bias.
  --score               Score the system parameters' prediction accuracy
                        throughout the season.
  -c, --crosstable      Generate expected outcomes in each maptype. Outputs to
                        Crosstable.csv.
  -t, --timeline        Generate rating history, taken at the end of every
                        rating period. Outputs to Timeline.csv.
  -p PERIOD, --periods PERIOD
                        Split the season into P rating periods. Default=25
  -r RATING, --rating RATING
                        Set the starting rating for each player. Default=1500
  -d DEV, --deviation DEV
                        Set the starting rating deviation for each player.
                        Default=400
  -v VOL, --volatility VOL
                        Set the starting volatility for each player.
                        Default=0.08

# bracket.py

Simulates playoff brackets for the 2019 season, outputs likelihood of each team earning each place in the bracket.

usage: bracket.py [-h] [-a A] [-s]

optional arguments:
  -h, --help       show this help message and exit
  -a A, --alpha A  Default 0. Factor to bias match outcome probabilities from
                   Crosstable values towards 50/50. 0<=a<=1
  -s, --seed       Add existing match outcomes before running bracket
                   simulations.
