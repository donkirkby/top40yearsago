import logging
import os
from datetime import datetime, timedelta

import requests
from mastodon import Mastodon

from validate_issues import parse_date_from_title, TZ, validate_issue

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def can_post(title: str, now: datetime = None):
    if now is None:
        now = datetime.now(TZ)
    post_date = parse_date_from_title(title)
    if post_date is None:
        return False
    post_date += timedelta(hours=post_date.day % 24)
    while post_date.hour < 6:
        post_date += timedelta(hours=12)
    while 18 <= post_date.hour:
        post_date -= timedelta(hours=12)
    return post_date <= now


def main():
    logger.info('Scanning issues to post.')
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
        try:
            validate_issue(issue)
        except ValueError:
            logger.warning('Invalid issue.', exc_info=True)
            continue
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
    logger.info(f'Toots: {toot_count}.')


if __name__ == '__main__':
    main()
