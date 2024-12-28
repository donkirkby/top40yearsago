import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from operator import itemgetter

from bs4 import BeautifulSoup
from mastodon import Mastodon


def main():
    mastodon_url = os.environ['TOP40URL']
    access_token = os.environ['TOP40ACCESSTOKEN']
    account_name = os.environ['TOP40ACCOUNTNAME']
    mastodon = Mastodon(api_base_url=mastodon_url,
                        access_token=access_token,
                        ratelimit_method='pace')
    accounts = mastodon.account_search(account_name)
    assert len(accounts) == 1
    account = accounts[0]

    user_reaction_count = Counter()
    tz = datetime.now(timezone.utc).astimezone().tzinfo
    today = datetime.now(tz)
    start_date = today - timedelta(days=366)
    report_interval = timedelta(weeks=4)
    report_date = today - report_interval
    all_toots = []
    max_id = None  # Start with latest
    is_finished = False
    reply_factor = 3
    while not is_finished:
        toots = mastodon.account_statuses(account, max_id=max_id, limit=100)
        for toot in toots:
            toot_created = toot['created_at']
            if toot_created < start_date:
                is_finished = True
                break
            if toot_created < report_date:
                print(f'Reached {report_date.strftime("%d %b %Y")}')
                report_date -= report_interval
            parsed = BeautifulSoup(toot['content'], 'html.parser')
            toot['plain_text'] = parsed.get_text()
            reblogs = mastodon.status_reblogged_by(toot)
            for reblog in reblogs:
                user_reaction_count[reblog['username']] += 1
            favourites = mastodon.status_favourited_by(toot)
            for favourite in favourites:
                user_reaction_count[favourite['username']] += 1
            blog_context = mastodon.status_context(toot)
            for descendant in blog_context['descendants']:
                user_reaction_count[descendant['account']['username']] += reply_factor
            all_toots.append(toot)
        max_id = toots[-1]['id']
    summary_count = 5
    print(f'Fetched {len(all_toots)} toots, '
          f'since {start_date.strftime("%d %b %Y")}.')
    for description, key_func in (('reactions', get_reaction_count),
                                  ('reblogs', itemgetter('reblogs_count')),
                                  ('favourites', itemgetter('favourites_count')),
                                  ('replies', itemgetter('replies_count'))):
        all_toots.sort(key=key_func, reverse=True)
        print('===')
        for toot in all_toots[:summary_count]:
            print(f'{key_func(toot)} {description},\n{toot["plain_text"]}\n')

    for username, count in user_reaction_count.most_common(summary_count):
        print(f'{username}: {count} reactions')


def get_reaction_count(toot: dict) -> int:
    return sum(toot[field] for field in ('replies_count',
                                         'reblogs_count',
                                         'favourites_count'))

if __name__ in ('__live_coding__', '__main__'):
    main()
