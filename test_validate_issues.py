from datetime import datetime, timedelta

import pytest

from validate_issues import validate_issue


@pytest.fixture
def next_week() -> str:
    return (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')


def test_non_post():
    issue = dict(title='No date',
                 body='lorem ipsum',
                 labels=[])

    validate_issue(issue)  # Doesn't raise error.


def test_good_post(next_week):
    issue = dict(title=f'{next_week} Regular YouTube',
                 body='Cool song, bro! https://youtube.com/watch?v=1234',
                 labels=[dict(name='post')])

    validate_issue(issue)  # Doesn't raise error.


def test_short_youtube(next_week):
    issue = dict(title=f'{next_week} Short YouTube',
                 body='Cool song, bro! https://youtu.be/1234',
                 labels=[dict(name='post')])

    validate_issue(issue)  # Doesn't raise error.


def test_date_without_label(next_week):
    issue = dict(title=f'{next_week} Has a date',
                 body='lorem ipsum',
                 labels=[])

    with pytest.raises(ValueError,
                       match=fr"Issue has a date, but no post label: "
                             fr"'{next_week} Has a date'\."):
        validate_issue(issue)


def test_label_without_date():
    issue = dict(title='No date',
                 body='lorem ipsum',
                 labels=[dict(name='post')])

    with pytest.raises(ValueError,
                       match=r"Issue has post label, but no date: 'No date'\."):
        validate_issue(issue)


def test_old_date():
    issue = dict(title='1984-01-01 Old Date',
                 body='lorem ipsum',
                 labels=[dict(name='post')])

    with pytest.raises(ValueError,
                       match=r"Post date is too old: '1984-01-01 Old Date'\."):
        validate_issue(issue)


def test_long_body(next_week):
    issue = dict(title=f'{next_week} Long Body',
                 body='X' * 501,
                 labels=[dict(name='post')])

    with pytest.raises(ValueError,
                       match=fr"Post body is 501 characters long: "
                             fr"'{next_week} Long Body'\."):
        validate_issue(issue)


def test_no_youtube(next_week):
    issue = dict(title=f'{next_week} No YouTube',
                 body='Cool song, bro!',
                 labels=[dict(name='post')])

    with pytest.raises(ValueError,
                       match=fr"Post has no YouTube link: "
                             fr"'{next_week} No YouTube'\."):
        validate_issue(issue)
