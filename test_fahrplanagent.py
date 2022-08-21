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
def ice1691():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 791', '7:33', '8:57', 14)


@pytest.fixture(scope='function')
def ice1691_fake():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 791', '6:33', '7:57', 14)


@pytest.fixture(scope='function')
def ice1691_late():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 791', '7:44', '8:57', 14)


@pytest.fixture(scope='function')
def ice1691_tc():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 791', '7:33', '8:57', 12)


@pytest.fixture(scope='function')
def ice1691_larr():
    return ExpectedTrain('Berlin Hbf', 'Braunschweig Hbf', 'ICE 791', '7:33', '8:47', 14)


@pytest.fixture(scope='function')
def ice1691_nostop():
    return ExpectedTrain('Berlin Hbf', 'Wolfsburg Hbf', 'ICE 791', '7:33', '8:57', 14)


def test_station_id(api):
    station_id = api.get_station_id('Berlin Hbf')
    assert (station_id == 8011160)


def test_train(api):
    date = datetime.date(2022, 8, 22)
    time = datetime.time(7, 00)
    train_id, time, track = api.get_train(8011160, date, time, 'ICE 791')
    assert (time == datetime.time(7, 33))
    assert (track == '14')


def test_train_fails(api):
    date = datetime.date(2022, 8, 22)
    time = datetime.time(8, 00)
    train_id, time, track = api.get_train(8011160, date, time, 'ICE 791')
    assert (train_id is None)


def test_stops(api):
    date = datetime.date(2022, 8, 22)
    time = datetime.time(7, 00)
    train_id, time, track = api.get_train(8011160, date, time, 'ICE 791')
    stops = [s['stopName'] for s in api.get_train_stops(train_id)]
    assert ('Braunschweig Hbf' in stops)


def test_expected_train(api, ice1691):
    ok = ice1691.check_for_date(api, datetime.date(2022, 8, 22))
    ice1691.print_status()
    assert (ok)


def test_expected_train_notfound(api, ice1691_fake):
    ok = ice1691_fake.check_for_date(api, datetime.date(2022, 8, 22))
    ice1691_fake.print_status()
    assert (not ok)


def test_expected_train_earlier(api, ice1691_late):
    ok = ice1691_late.check_for_date(api, datetime.date(2022, 8, 22))
    ice1691_late.print_status()
    assert (not ok)
    assert (not ice1691_late.ontime[0])
    assert (ice1691_late.ontime[1] == datetime.time(7, 33))


def test_expected_train_trackchange(api, ice1691_tc):
    ok = ice1691_tc.check_for_date(api, datetime.date(2022, 8, 22))
    ice1691_tc.print_status()
    assert (not ok)
    assert (not ice1691_tc.ontrack[0])
    assert (ice1691_tc.ontrack[1] == '14')


def test_expected_train_nostop(api, ice1691_nostop):
    ok = ice1691_nostop.check_for_date(api, datetime.date(2022, 8, 22))
    ice1691_nostop.print_status()
    assert (not ok)
    assert (not ice1691_nostop.has_destination)


def test_expected_train_latearrival(api, ice1691_larr):
    ok = ice1691_larr.check_for_date(api, datetime.date(2022, 8, 22))
    ice1691_larr.print_status()
    assert (not ok)
    assert (not ice1691_larr.arrival_ontime[0])
    assert (ice1691_larr.arrival_ontime[1] == datetime.time(8, 57))
