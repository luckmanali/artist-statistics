# Artist Statistics
A simple cli program that takes the name of an artist and produces some statistics based on the number of words in their songs.

## Installation
Click `clone/download`, unzip file

## What do i need to run this?
Python 3.7.4, Requests, Argparse

- To install Python: https://www.python.org/
- To install the requirements open a CMD/Terminal and type the following: 

```
cd "directory you saved the .zip file"
cd artist-statistics
pip install -r requirements.txt
```


## Execution

To run this program you need to call it while passing in the name of an artist as the first argument. All other arguments are optional.

```
cd "directory you saved the .zip file"
cd artist-statistics

# to get the usage details:
python main.py --help

# or use -h for the shortcut
python main.py -h

# to examine an artist:
python main.py [artist]

# to compare artists:
python main.py [artist] --compare [artist2]

# or use -c for the shortcut
python main.py [artist] -c [artist2]

# to increase the limit of tracks analysed (default: 25 max:100):
python main.py [artist] --limit [limit]

# or use -l for the shortcut
python main.py [artist] -l [limit]

# to return all tracks:
python main.py [artist] --all

# or use -a for the shortcut:
python main.py [artist] -a
```

## TODO
- [ ] Create a graphical user interface (GUI)
- [ ] Change in average by album/year etc.
- [ ] Visualisations (charts & graphs)
- [ ] Build unit tests