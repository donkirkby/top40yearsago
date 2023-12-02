import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from mastodon import Mastodon

TZ = ZoneInfo('America/Vancouver')


def can_post(title: str, now: datetime = None):
    if now is None:
        now = datetime.now(TZ)
    try:
        post_date = datetime.strptime(title[:10],'%Y-%m-%d')
        post_date = post_date.replace(tzinfo=TZ)
    except ValueError:
        # If it doesn't start with a date, we can't post it.
        return False
    post_date += timedelta(hours=post_date.day % 24)
    while post_date.hour < 6:
        post_date += timedelta(hours=12)
    while 18 <= post_date.hour:
        post_date -= timedelta(hours=12)
    return post_date <= now


def main():
    mastodon_url = os.environ['TOP40URL']
    access_token = os.environ['TOP40ACCESSTOKEN']
    mastodon = Mastodon(api_base_url=mastodon_url,
                        access_token=access_token)
    github_repo = os.environ['GITHUBREPO']
    github_token = os.environ['GITHUBTOKEN']
    authorization_header = {'Authorization': f'Bearer {github_token}'}
    url = f'https://api.github.com/repos/{github_repo}/issues?labels=post'
    response = requests.get(url, headers=authorization_header)
    response.raise_for_status()
    toot_count = 0
    for issue in response.json():
        title: str = issue['title']
        body = issue['body']
        if can_post(title):
            issue_url = issue['url']
            response = requests.patch(issue_url,
                                      json=dict(state='closed'),
                                      headers=authorization_header)
            response.raise_for_status()
            mastodon.status_post(body)
            toot_count += 1
    print(f'Toots: {toot_count}.')


if __name__ == '__main__':
    main()
