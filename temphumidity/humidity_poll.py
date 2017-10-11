#!/usr/bin/env python3.5
"""
humidity_poll.py
A new implmentation of the `dht-sensors.py` script cleaning up
a lot of the old stuff and switching to using PostgreSQL.

Author: Lucas Salibian
"""

from sys import argv
import signal
import datetime
import time
import pytz
import json
import logging

import psycopg2 as pg

try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warn("Failed to import GPIO")

try:
    import Adafruit_DHT as DHT
except ImportError:
    logging.warn("Failed to import Adafruit_DHT")

timezone = pytz.timezone("America/Vancouver")


def load_config(config_file="/etc/humidity-poll/config.json"):
    with open(config_file, "r") as fd:
        return json.load(fd)


def get_sensor_data(sensor_id):
    humidity, temperature = DHT.read_retry(DHT.DHT22, sensor_id)
    return humidity, temperature


def new_sensor(sensor_id, batch_id):
    yield 'ok'
    while True:
        humidity, temp = get_sensor_data(sensor_id)
        yield (batch_id, humidity, temp)


def connect_db(cfg):
    conn = pg.connect(
        dbhost=cfg.get('dbhost', None),
        user=cfg['dbuser'],
        dbname=cfg['dbname'],
        dbpassword=cfg.get('dbpassword', None)
    )
    return conn


def insert_entry(cfg, batch_id, temp, humidity):
    with connect_db(cfg) as conn:
        with conn.cursor() as cur:
            ts = datetime.datetime.now(timezone)
            cur.execute(
                "INSERT INTO sensor_data (ts, temp, humidity, batch) VALUES (%s, %s, %s, %s)",
                (ts,
                 temp,
                 humidity,
                 batch_id)
            )
        conn.commit()


def create_new_batch(cfg, name, location):
    with connect_db(cfg) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO batches (name, location, created) VALUES (%s, %s, clock_timestamp()",
                (name, location)
            )
        conn.commit()


def signal_handler(sig, _frame):
    logging.error("Signal %s recieved. Terminating.", sig)
    raise IOError(sig)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    config_path = "/etc/humidity-poll/config.json"
    if len(argv) > 1:
        config_path = argv[1]

    cfg = load_config(config_path)
    sensors = list(map(lambda sensor: new_sensor(
        sensor['sensor_id'], sensor['batch_id']), cfg['sensors']))

    # Ensure that the generator is working as expected.
    for s in sensors:
        value = next(s)
        if value != "ok":
            raise Exception("failed initial yield")

    while True:
        for s in sensors:
            batch_id, humidity, temp = next(s)
            logging.info(
                "Pushing message batch_id: %s, temp: %s, humidity: %s", batch_id, temp, humidity)
            try:
                insert_entry(cfg, batch_id, temp, humidity)
            except:
                logging.error("Failed to connect to database")
        time.sleep(cfg.get('fetch_delay', 10000) / 1000)

    logging.info("All sensors ready...")

    return


if __name__ == "__main__":
    main()
