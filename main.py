"""
A simple cli program that takes the name of an artist and produces some statistics
based on the number of words in their songs.

To run this program you need to call it while passing in the name of the artist as the first argument.
All other arguments are optional.

Arguments:
    artist (str): the name of an artist you wish to examine                                     [[REQUIRED]]
    --compare [artist] (str): the name of the artist you wish to compare with                   [[OPTIONAL]]
    --limit [limit] (int): the number of tracks you want to analyse (default: 25, max: 100)     [[OPTIONAL]]
    --all: performs analysis on all the available songs (overrides the limit argument)          [[OPTIONAL]]
    --help: prints usage and quits the program
"""

import json
import argparse
import time
import sys
from statistics import variance, stdev
import requests
from concurrent.futures import ThreadPoolExecutor


# Setting up the arguments that are passed into the program
parser = argparse.ArgumentParser(
    description='This program takes the name of an artist '
                'and produces the average, the min and the max number of words in their songs, '
                'it will also calculate the variance and standard deviation. '
                'If an additional artist is provided it will compare the values.')

parser.add_argument("artist", type=str, help="the name of an artist you wish to examine")
parser.add_argument("-c", "--compare", type=str, help="the name of the artist you wish to compare with")
parser.add_argument('-l', '--limit', type=int, default=25,
                    help='the number of tracks you want to analyse (default: 25, max: 100)')
parser.add_argument('-a', '--all', default=False, action='store_true',
                    help="performs analysis on all the available songs (overrides the limit argument)")

args = parser.parse_args()

get_all_tracks = False

if args.all:
    limit = 'all'
    get_all_tracks = True
else:
    # Making sure the limit does not exceed 100
    limit = (100, args.limit)[args.limit <= 100]


class Artist:
    """
    This class represents an artist and the relevant track details/statistics
    """
    def __init__(self, artist_name):
        self.artist_name = artist_name.title()
        self.tracks = self._get_artist_recordings()
        self.values = self._get_length_of_tracks()

        self.average = round(sum(self.values) / len(self.values), 2)
        self.max = max(self.values)
        self.min = min(self.values)
        self.variance = variance(self.values)
        self.standard_deviation = stdev(self.values)

    @staticmethod
    def _get_word_count_from_track(url):
        """
        Requests lyrics for a track and returns the total number of words.
        :param url: str
        :return: int
        """
        response = requests.get(url, headers={'Content-Type': "application/json", "connection": "keep-alive"},
                                timeout=5)

        if response.status_code == 200:
            return len(json.loads(response.text)['lyrics'].replace('\n', ' ').split(' '))

    def _get_length_of_tracks(self):
        """
        Creates a list of url get requests and executes them
        :return: list
        """
        urls = []
        for track_title in self.tracks:
            urls.append(f'https://api.lyrics.ovh/v1/{self.artist_name}/{track_title}')

        with ThreadPoolExecutor() as executor:
            values = executor.map(self._get_word_count_from_track, urls)

        values = list(filter(None, values))

        if not values:
            print(f"No lyrics found for the artist {self.artist_name}, did you spell the artist name correctly?")
            sys.exit(1)
        return values

    def _get_recording_data(self, offsets):
        """
        The Musicbrainz API only returns a maximum of 100 records per request,
        this function makes a request with an offset to the records returned.
        :param offsets: int
        :return: dict
        """
        params = {"query": f"artist:{self.artist_name}", "limit": 100, 'offset': offsets}
        response = requests.get(r'https://musicbrainz.org/ws/2/recording',
                                headers={"Application": "name:anonymous", "Accept": "application/json"},
                                params=params, timeout=5)
        data = json.loads(response.text)
        return data.get('recordings', None)

    def _get_artist_recordings(self):
        """
        Requests a list of track names for the artist
        :return: list
        """
        base_url = r'https://musicbrainz.org/ws/2/'

        headers = {
            "Application": "name:anonymous",
            "Accept": "application/json"
        }

        params = {
            "query": f"artist:{self.artist_name}",
            "limit": limit,  # Set the number of returned values to 100
        }

        response = requests.get(f'{base_url}recording', headers=headers, params=params)
        data = json.loads(response.text)

        if data.get('count') == 0:
            print(f"Could not find any tracks for {self.artist_name}, did you spell the artist name correctly?")
            sys.exit(1)

        if get_all_tracks:
            count = int(data.get('count')/100)
            print(f'Found {data.get("count")} tracks')
            print(f'Analysing, please wait this can take awhile...')

            offsets = []
            for i in range(count):
                offsets.append(100 * i)

            with ThreadPoolExecutor() as executor:
                # get a list of track names from the data
                recordings = executor.map(self._get_recording_data, offsets)

                recordings = list(filter(None, recordings))

                track_names = []
                for response in recordings:
                    for dict in response:
                        track_names.append(dict['title'])
        else:
            recordings = data['recordings']
            recordings = list(filter(None, recordings))
            track_names = [track['title'] for track in recordings]

        # remove any duplicates
        return set(track_names)

    def print_details(self):
        """
        Prints the artists name along with some statistics from the number of words in their songs.
        :return: None
        """
        print(
            f'Artist name: {self.artist_name} \n'
            f'Average length of songs: {self.average} \n'
            f'Max words in single song: {self.max} \n'
            f'Min words in single song: {self.min} \n'
            f'The variance is: {self.variance} \n'
            f'The standard deviation is: {self.standard_deviation} \n'
        )

    def print_difference(self, artist_object):
        """
        Prints the difference between statistics compared with another artist
        :param artist_object: An instance of the Artist class
        :return: None
        """
        print(
            f'Comparing artists: {self.artist_name} and {artist_object.artist_name} \n'
            f'The difference in the average is: {abs(artist_object.average-self.average)} \n'
            f'The difference in the max length is: {abs(artist_object.max-self.max)} \n'
            f'The difference in the min length is: {abs(artist_object.min-self.min)} \n'
            f'The difference in the variance is: {abs(artist_object.variance-self.variance)} \n'
            f'The difference in the standard deviation is: {abs(artist_object.standard_deviation-self.standard_deviation)} \n'
        )


def print_banner(title):
    """
    Prints a banner with the given title
    :param title: str
    :return: None
    """
    print("-" * len(title))
    print(title)
    print("-" * len(title))


def main():
    """
    Starts the program
    :return: None
    """
    print_banner("AireLogic Tech Test by Luckman Ali")
    print(f'Collecting {limit} tracks, please wait...')

    artist = Artist(args.artist)

    if args.compare:
        artist.print_difference(Artist(args.compare))
    else:
        artist.print_details()


if __name__ == '__main__':
    start = time.perf_counter()
    main()
    finish = time.perf_counter()
    print(f"--- Finished in {round(finish-start, 2)} seconds ---")
