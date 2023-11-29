from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from datetime import datetime, timedelta
from operator import attrgetter

import pandas as pd
from pandas import DataFrame

DATE_DISPLAY_FORMAT = '%d %b %Y'
DATE_STORED_FORMAT = '%-m/%-d/%Y'


def parse_args():
    today = datetime.today()
    try:
        default_date = today.replace(year=today.year - 40)
    except ValueError:
        # Leap year
        default_date = today.replace(year=today.year - 40, day=today.day - 1)
    known_date = datetime(1979, 9, 1)
    days_offset = default_date - known_date
    default_date += timedelta(days=7-(days_offset.days % 7))
    default_date_text = default_date.strftime(DATE_DISPLAY_FORMAT)

    # noinspection PyTypeChecker
    parser = ArgumentParser(description='Find top 40 events from 40 years ago.',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('date',
                        help='date to scan',
                        nargs='?',
                        type=parse_date,
                        default=default_date_text)
    return parser.parse_args()


def parse_date(date_text: str):
    return datetime.strptime(date_text, DATE_DISPLAY_FORMAT)


def find_diffs(max_position, min_peak, base, other, all_weeks):
    """ Report changes in a certain range.

    :param max_position: the maximum position to report (40 for top 40)
    :param min_peak: the minimum peak position to report (excluded)
    :param base: data frame holding the current week's songs
    :param other: data frame holding the previous week's songs
    :param all_weeks: data frame holding songs for all weeks
    """
    top_base = base[base['week_position'] <= max_position]
    top_other = other[other['week_position'] <= max_position]
    added_song_ids = set(top_base['songid']) - set(top_other['songid'])
    added_songs = base[base['songid'].isin(added_song_ids)].sort_values('all_time_peak')
    display_songs(f'entered the #Top{max_position}', added_songs, all_weeks, min_peak)


def main():
    args = parse_args()
    print(f'Events for the week of {args.date.strftime(DATE_DISPLAY_FORMAT)}:')
    # url,WeekID,Week Position,Song,Performer,SongID,Instance,Previous Week Position,Peak Position,Weeks on Chart
    all_weeks = pd.read_csv('hot100.csv')
    all_weeks = all_weeks.rename(
        columns=lambda label: label.lower().replace(' ', '_'))
    all_weeks['all_time_peak'] = 0
    week_text = args.date.strftime(DATE_STORED_FORMAT)
    week_df: DataFrame = all_weeks[all_weeks['weekid'] == week_text].copy()
    if week_df.empty:
        exit(f'No data found for {week_text}.')
    prev_week_text = (args.date-timedelta(days=7)).strftime(DATE_STORED_FORMAT)
    prev_week_df = all_weeks[all_weeks['weekid'] == prev_week_text].copy()
    if prev_week_df.empty:
        exit(f'No data found for {prev_week_text}.')

    find_diffs(100, 40, week_df, prev_week_df, all_weeks)
    find_diffs(40, 10, week_df, prev_week_df, all_weeks)
    find_diffs(10, 1, week_df, prev_week_df, all_weeks)
    find_diffs(1, 0, week_df, prev_week_df, all_weeks)
    find_diffs(1, 0, prev_week_df, week_df, all_weeks)


def display_performer(performer: str) -> str:
    return '#' + performer.replace(' ', '')


def display_songs(heading, songs, all_weeks, min_peak):
    if not songs.empty:
        print(heading)
        displays = []
        stored_format = DATE_STORED_FORMAT.replace('-', '')
        for song in songs.itertuples():
            display = Namespace(song=song)
            song_entries = all_weeks[all_weeks['songid'] == song.songid]
            song_entries = song_entries.sort_values(['instance',
                                                     'weeks_on_chart'])
            positions = []
            peak_pos = None
            peak_date = None
            for song_entry in song_entries.itertuples():
                if peak_pos is None or song_entry.week_position < peak_pos:
                    peak_date = song_entry.weekid
                    peak_pos = song_entry.week_position
                prefix = '#' if song_entry.weekid == song.weekid else ''
                pos_text = ('*'*(song_entry.instance-1) +
                            prefix +
                            str(song_entry.week_position))
                positions.append(pos_text)
            display.peak_position = peak_pos
            display.peak_date = datetime.strptime(peak_date, stored_format)
            display.positions = positions
            if peak_pos > min_peak:
                displays.append(display)
        displays.sort(key=attrgetter('peak_position'))
        for display in displays:
            song = display.song
            performer = display_performer(song.performer)
            print(f'40 years ago this week, "{song.song}" by {performer} '
                  f'{heading} at {song.week_position}. It peaked at '
                  f'{display.peak_position} on '
                  f'{display.peak_date.strftime(DATE_DISPLAY_FORMAT)}. #1980s '
                  f'#musichistory #musicvideo')
            print(', '.join(display.positions))
        print()


main()
