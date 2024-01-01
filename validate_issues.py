import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

TZ = ZoneInfo('America/Vancouver')
CUTOFF_DATE = datetime.now(tz=TZ) - timedelta(days=180)


def parse_date_from_title(title: str) -> datetime | None:
    try:
        post_date = datetime.strptime(title[:10], '%Y-%m-%d')
        post_date = post_date.replace(tzinfo=TZ)
    except ValueError:
        # If it doesn't start with a date, we can't post it.
        return None
    return post_date


def validate_issue(issue: dict):
    date = parse_date_from_title(issue['title'])
    is_post = any(label['name'] == 'post' for label in issue['labels'])
    if date is None:
        if is_post:
            raise ValueError(f'Issue has post label, but no date: {issue["title"]!r}.')
        return
    if not is_post:
        message = f'Issue has a date, but no post label: {issue["title"]!r}.'
        raise ValueError(message)
    if date < CUTOFF_DATE:
        raise ValueError(f'Post date is too old: {issue["title"]!r}.')
    body_length = len(issue['body'])
    if body_length > 500:
        raise ValueError(f'Post body is {body_length} characters long: '
                         f'{issue["title"]!r}.')
    if re.search(r'https?://(www\.)?(youtube\.com|youtu\.be)',
                 issue['body']) is None:
        raise ValueError(f'Post has no YouTube link: {issue["title"]!r}.')


def main():
    github_repo = os.environ['GITHUBREPO']
    url = f'https://api.github.com/repos/{github_repo}/issues'
    response = requests.get(url)
    response.raise_for_status()
    issues = response.json()
    for issue in issues:
        validate_issue(issue)
    print(f'Validated {len(issues)} issues.')


if __name__ == '__main__':
    main()
