#!/usr/bin/env python

import datetime
import pytest

from fahrplanagent import *


def test_datetime_from_iso():
    dt = datetime_from_iso("2017-05-03T07:34")
    assert dt.year == 2017
    assert dt.month == 5
    assert dt.day == 3
    assert dt.hour == 7
    assert dt.minute == 34


def test_time_from_iso():
    dt = time_from_iso("07:34")
    assert dt.hour == 7
    assert dt.minute == 34
    dt = time_from_iso("7:34")
    assert dt.hour == 7
    assert dt.minute == 34


def test_time_minus_30():
    dt = time_from_iso("07:34")
    tt = time_minus_30(dt)
    assert tt == time_from_iso("07:04")
    dt = time_from_iso("07:04")
    tt = time_minus_30(dt)
    assert tt == time_from_iso("06:34")


@pytest.fixture
def api():
    return FahrplanAPI()


@pytest.fixture(scope='function')
def ice595():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 595', '7:34', '8:56', 14)


@pytest.fixture(scope='function')
def ice595_fake():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 595', '6:34', '7:56', 14)


@pytest.fixture(scope='function')
def ice370():
    return ExpectedTrain('Braunschweig Hbf', 'Berlin Hbf', 'ICE 370', '15:59', '17:28', 7)


def test_station_id(api):
    station_id = api.get_station_id('Berlin Hbf')
    assert (station_id == 8011160)


def test_train(api):
    date = datetime.date(2017, 5, 3)
    time = datetime.time(7, 00)
    train_id, time, track = api.get_train(8011160, date, time, 'ICE 595')
    assert (time == datetime.time(7, 34))
    assert (track == '14')


def test_train_fails(api):
    date = datetime.date(2017, 5, 3)
    time = datetime.time(8, 00)
    train_id, time, track = api.get_train(8011160, date, time, 'ICE 595')
    assert (train_id is None)


def test_stops(api):
    date = datetime.date(2017, 5, 3)
    time = datetime.time(7, 00)
    train_id, time, track = api.get_train(8011160, date, time, 'ICE 595')
    stops = [s['stopName'] for s in api.get_train_stops(train_id)]
    assert ('Braunschweig Hbf' in stops)


def test_expected_train(api, ice595):
    ok = ice595.check_for_date(api, datetime.date(2017, 5, 3))
    ice595.print_status()
    assert (ok)


def test_expected_train_notfound(api, ice595_fake):
    ok = ice595_fake.check_for_date(api, datetime.date(2017, 5, 3))
    ice595_fake.print_status()
    assert (not ok)


def test_expected_train_earlier(api, ice595):
    ok = ice595.check_for_date(api, datetime.date(2017, 5, 22))
    ice595.print_status()
    assert (not ok)
    assert (not ice595.ontime[0])
    assert (ice595.ontime[1] == datetime.time(7, 23))


def test_expected_train_trackchange(api, ice595):
    ok = ice595.check_for_date(api, datetime.date(2017, 5, 22))
    ice595.print_status()
    assert (not ok)
    assert (not ice595.ontrack[0])
    assert (ice595.ontrack[1] == '5')


def test_expected_train_nostop(api, ice595):
    ok = ice595.check_for_date(api, datetime.date(2017, 5, 10))
    ice595.print_status()
    assert (not ok)
    assert (not ice595.has_destination)


def test_expected_train_latearrival(api, ice370):
    ok = ice370.check_for_date(api, datetime.date(2017, 5, 22))
    ice370.print_status()
    assert (not ok)
    assert (not ice370.arrival_ontime[0])
    assert (ice370.arrival_ontime[1] == datetime.time(17, 35))
