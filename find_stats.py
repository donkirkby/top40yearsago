from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from datetime import datetime, timedelta
from operator import attrgetter

import pandas as pd
from pandas import DataFrame

DATE_DISPLAY_FORMAT = '%d %b %Y'
DATE_STORED_FORMAT = '%Y-%m-%d'


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
    top_base = base[base['chart_position'] <= max_position]
    top_other = other[other['chart_position'] <= max_position]
    added_song_ids = set(top_base['song_id']) - set(top_other['song_id'])
    added_songs = base[base['song_id'].isin(added_song_ids)].sort_values('all_time_peak')
    display_songs(f'entered the #Top{max_position}', added_songs, all_weeks, min_peak)


def main():
    args = parse_args()
    print(f'Events for the week of {args.date.strftime(DATE_DISPLAY_FORMAT)}:')
    # chart_position,chart_date,song,performer,song_id,instance,time_on_chart,
    # consecutive_weeks,previous_week,peak_position,worst_position,chart_debut,
    # chart_url
    all_weeks = pd.read_csv('hot100.csv')
    all_weeks = all_weeks.rename(
        columns=lambda label: label.lower().replace(' ', '_'))
    all_weeks['all_time_peak'] = 0
    week_text = args.date.strftime(DATE_STORED_FORMAT)
    week_df: DataFrame = all_weeks[all_weeks['chart_date'] == week_text].copy()
    if week_df.empty:
        exit(f'No data found for {week_text}.')
    prev_week_text = (args.date-timedelta(days=7)).strftime(DATE_STORED_FORMAT)
    prev_week_df = all_weeks[all_weeks['chart_date'] == prev_week_text].copy()
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
        for song in songs.itertuples():
            display = find_peak(song, all_weeks)
            if display.peak_position > min_peak:
                displays.append(display)
        displays.sort(key=attrgetter('peak_position'))
        for display in displays:
            song = display.song
            performer = display_performer(song.performer)
            print(f'40 years ago this week, "{song.song}" by {performer} '
                  f'{heading} at {song.chart_position}. It peaked at '
                  f'{display.peak_position} on '
                  f'{display.peak_date.strftime(DATE_DISPLAY_FORMAT)}. #1980s '
                  f'#MusicHistory #MusicVideo')
            print(', '.join(display.positions))
            performer_history_displays = []
            performer_songs = all_weeks[all_weeks['performer'] == song.performer]
            for other_song_name, other_song_entries in performer_songs.groupby('song'):
                other_song = next(other_song_entries.itertuples())
                other_display = find_peak(other_song, other_song_entries)
                performer_history_displays.append(other_display)
            performer_history_displays.sort(key=attrgetter('peak_date'))
            performer_history = []
            for other_display in performer_history_displays:
                other_date_display = other_display.peak_date.strftime(DATE_DISPLAY_FORMAT)
                performer_history.append(f'{other_display.song.song} '
                                         f'#{other_display.peak_position} '
                                         f'on {other_date_display}')
            print(', '.join(performer_history))
        print()


def find_peak(song, all_weeks):
    chart_date = song.chart_date
    display = Namespace(song=song)
    song_entries = all_weeks[all_weeks['song_id'] == song.song_id]
    song_entries = song_entries.sort_values(['instance',
                                             'time_on_chart'])
    positions = []
    peak_pos = None
    peak_date = None
    for song_entry in song_entries.itertuples():
        if peak_pos is None or song_entry.chart_position < peak_pos:
            peak_date = song_entry.chart_date
            peak_pos = song_entry.chart_position
        prefix = '#' if song_entry.chart_date == chart_date else ''
        pos_text = ('*' * (song_entry.instance - 1) +
                    prefix +
                    str(song_entry.chart_position))
        positions.append(pos_text)
    stored_format = DATE_STORED_FORMAT  # .replace('-', '')
    display.peak_position = peak_pos
    display.peak_date = datetime.strptime(peak_date, stored_format)
    display.positions = positions
    return display


main()
