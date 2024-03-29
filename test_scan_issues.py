from datetime import datetime

import pytest

from scan_issues import can_post, TZ


def test_current_time_past():
    title = '2000-01-01 Example'

    assert can_post(title)


def test_current_time_future():
    title = '3000-01-01 Example'

    assert not can_post(title)


@pytest.mark.parametrize('now_text,should_post',
                         [('2020-06-05 23:59', False),
                          ('2020-06-07 00:00', True),
                          ('2020-06-06 05:59', False),
                          ('2020-06-06 06:00', True)])
def test_after_six_am(now_text, should_post):
    now = datetime.strptime(now_text, '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
    title = '2020-06-06 Example'
    decision = can_post(title, now)
    assert decision == should_post


@pytest.mark.parametrize('now_text,should_post',
                         [('2020-06-05 16:59', False),
                          ('2020-06-05 17:00', True)])
def test_before_six_am(now_text, should_post):
    now = datetime.strptime(now_text, '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
    title = '2020-06-05 Example'
    decision = can_post(title, now)
    assert decision == should_post


@pytest.mark.parametrize('now_text,should_post',
                         [('2020-06-18 05:59', False),
                          ('2020-06-18 06:00', True)])
def test_after_six_pm(now_text, should_post):
    now = datetime.strptime(now_text, '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
    title = '2020-06-18 Example'
    decision = can_post(title, now)
    assert decision == should_post


@pytest.mark.parametrize('now_text,should_post',
                         [('2020-06-25 12:59', False),
                          ('2020-06-25 13:00', True)])
def test_late_in_month(now_text, should_post):
    now = datetime.strptime(now_text, '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
    title = '2020-06-25 Example'
    decision = can_post(title, now)
    assert decision == should_post


def test_no_date():
    title = 'No date example'
    assert not can_post(title)
