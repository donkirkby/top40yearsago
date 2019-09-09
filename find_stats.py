import pandas as pd


def find_all_time_peaks(current_week: pd.DataFrame, all_weeks: pd.DataFrame):
    current_week.set_index('songid', inplace=True)
    peak_positions = all_weeks[all_weeks['songid'].isin(
        current_week.index)].groupby('songid').min()
    current_week['all_time_peak'] = peak_positions['peak_position']
    current_week.sort_values(['all_time_peak', 'week_position'])


def find_diffs(max_position, base, other, title):
    top_base = base[base['week_position'] <= max_position]
    top_other = other[other['week_position'] <= max_position]
    added_song_ids = set(top_base.index) - set(top_other.index)
    added_songs = base[base.index.isin(added_song_ids)].sort_values('all_time_peak')
    display_songs(f'{title} in top {max_position}', added_songs)
    print()


def main():
    # url,WeekID,Week Position,Song,Performer,SongID,Instance,Previous Week Position,Peak Position,Weeks on Chart
    df = pd.read_csv('hot100.csv')
    df = df.rename(columns=lambda label: label.lower().replace(' ', '_'))
    df['all_time_peak'] = 0
    week_df = df[df['weekid'] == '9/8/1979'].copy()
    find_all_time_peaks(week_df, df)
    prev_week_df = df[df['weekid'] == '9/1/1979'].copy()
    find_all_time_peaks(prev_week_df, df)

    find_diffs(100, week_df, prev_week_df, 'New songs')
    find_diffs(40, week_df, prev_week_df, 'New songs')
    find_diffs(10, week_df, prev_week_df, 'New songs')
    find_diffs(100, prev_week_df, week_df, 'Dropped songs')
    find_diffs(40, prev_week_df, week_df, 'Dropped songs')
    find_diffs(10, prev_week_df, week_df, 'Dropped songs')

    # dropped_song_ids = set(prev_week_df['songid'])- set(week_df['songid'])
    # dropped_songs = prev_week_df[prev_week_df['songid'] in dropped_song_ids]
    # print('\n'.join(sorted(dropped_songs)))


def display_songs(heading, songs):
    if not songs.empty:
        print(heading)
        for song in songs.itertuples():
            print(f'{song.song} at #{song.week_position} by {song.performer} '
                  f'peaked at {song.all_time_peak}')


main()
