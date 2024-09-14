## FOOTSTATS

This simple program allows you to store football match data taken from [understat](https://understat.com/). It generates a .json file that stores the average expected goals, the average evaluation and the final normalized score per game and creates a leaderboard based on those parameters without considering the usual points gained per match.

The evaluation score is calculated as follows:

```math
Eval = \sum_{shots} ( Effective goal per shot - xG per shot )
```

The normalized score is calculated as follows:

```math
Sides = Shots on target \times 0.1 + Total shots \times 0.05 + \frac{1}{ppda}
```
```math
Norm = \frac{Eval + Sides}{Total xG + Sides} \times 10
```

Where 'ppda' stands for "Passes allowed per defensive action in the oppostition half".

This program keeps track of the performance of the offensive side of every team.

### USAGE

```shell
pip install -r requirements.txt
python main.py
```

Alternatively you can compile "main.py" with pyinstaller and run the executable located in the "dist" folder.

```shell
pyinstaller main.py --onefile
```
