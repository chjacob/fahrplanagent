#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fahrplan Agent - Informiert ueber DB Fahrplanaenderungen
#
#
# Copyright (C) 2017  Christoph Jacob (christoph.jacob@gmail.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import datetime

import urllib.request, urllib.parse, urllib.error
import requests

class API_Error(Exception):
    pass


def datetime_from_iso(iso_str):
    return datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M")


def time_from_iso(iso_str):
    hh, mm = iso_str.split(':')
    return datetime.time(int(hh), int(mm))


def time_minus_30(time):
    hh = time.hour
    mm = time.minute
    mm = mm - 30
    if mm < 0:
        mm = mm + 60
        hh = hh - 1
    return datetime.time(hh, mm)


class FahrplanAPI:

    def __init__(self):
        progdir = os.path.abspath(os.path.dirname(__file__))
        try:
            f = open(os.path.join(progdir, 'fahrplanapi-client-id.txt'))
            self.client_id = f.read().strip()
            f.close()

            f = open(os.path.join(progdir, 'fahrplanapi-client-secret.txt'))
            self.client_secret = f.read().strip()
            f.close()

            self.url = 'https://apis.deutschebahn.com/db-api-marketplace/apis/fahrplan/v1/'

        except IOError:
            raise API_Error("Access data for Fahrplan API required.")

    def make_request(self, type, query, params=None):
        url = self.url + type + '/'
        url = url + urllib.parse.quote(str(query))

        headers = {'DB-Client-Id': self.client_id,
                   'DB-Api-Key': self.client_secret,
                   'accept': "application/json"}

        r = requests.get(url, params=params, headers=headers)
        if not r.status_code == 200:
            print(r.status_code, r.json())
            raise API_Error("Fahrplan-API request failed")
        return r.json()

    def get_station_id(self, name):
        res = self.make_request('location', name)
        for station in res:
            if station['name'] == name:
                return station['id']

    def get_train(self, station_id, date, time, number):
        dt = datetime.datetime.combine(date, time)
        res = self.make_request('departureBoard', station_id,
                                params={'date': dt.isoformat()})
        for train in res:
            if train['name'] == number:
                time = datetime_from_iso(train['dateTime']).time()
                return train['detailsId'], time, train.get('track', 0)
        return None, None, None

    def get_train_stops(self, train_id):
        return self.make_request('journeyDetails', train_id)


class ExpectedTrain:

    def __init__(self, departure, destination, number, deptime, arrtime, track):
        self.departure = departure
        self.destination = destination
        self.number = number
        self.deptime = time_from_iso(deptime)
        self.arrtime = time_from_iso(arrtime)
        self.track = str(track)

        self.ontime = None
        self.arrival_ontime = None
        self.ontrack = None
        self.has_destination = None

    def check_for_date(self, api, date):
        station_id = api.get_station_id(self.departure)

        tt = self.deptime
        train_id = None
        while (train_id is None) and (tt.hour > 4):
            train_id, deptime, track = api.get_train(station_id, date, tt, self.number)
            tt = time_minus_30(tt)

        if train_id is None:
            self.ontime = (False, None)
            self.ontrack = (False, None)
            self.has_destination = False
        else:
            stops = api.get_train_stops(train_id)

            if self.deptime == deptime:
                self.ontime = (True,)
            else:
                self.ontime = (False, deptime)

            if self.track == track:
                self.ontrack = (True,)
            else:
                self.ontrack = (False, track)

            self.has_destination = False
            for stop in stops:
                if stop['stopName'].startswith(self.destination):
                    self.has_destination = True
                    arrtime = time_from_iso(stop['arrTime'])

            if self.has_destination:
                if self.arrtime == arrtime:
                    self.arrival_ontime = (True,)
                else:
                    self.arrival_ontime = (False, arrtime)
            else:
                self.arrival_ontime = (False, None)

        return self.all_ok()

    def all_ok(self):
        return (self.ontime[0] and self.arrival_ontime[0] and
                self.ontrack[0] and self.has_destination)

    def print_info(self, file=None):
        print(self.number, "um %02i:%02i" % (self.deptime.hour, self.deptime.minute),
              "(%s -> %s), Gleis %s" % (self.departure, self.destination, self.track),
              file=file)

    def print_status(self, file=None):
        if self.all_ok():
            print("    Zug verkehrt planmäßig", file=file)
        elif not self.ontime[0] and self.ontime[1] is None:
            print("    Zug fällt aus / Zug nicht gefunden", file=file)
        else:

            if not self.has_destination:
                print("    Ohne Halt in", self.destination, file=file)

            if self.ontime[0]:
                print("    Abfahrtszeit planmässig", file=file)
            elif self.ontime[1] is not None:
                print("    Abfahrtszeit abweichend um %02i:%02i" %
                      (self.ontime[1].hour, self.ontime[1].minute), file=file)

            if not self.ontrack[0]:
                print("    Abweichend von Gleis", self.ontrack[1], file=file)

            if self.has_destination and (not self.arrival_ontime[0]):
                print("    Ankunftszeit abweichend um %02i:%02i" %
                      (self.arrival_ontime[1].hour, self.arrival_ontime[1].minute),
                      " (statt %02i:%02i) " % (self.arrtime.hour, self.arrtime.minute),
                      file=file)
