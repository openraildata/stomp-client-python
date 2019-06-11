#
# National Rail Open Data client demonstrator
# Copyright (C)2019 OpenTrainTimes Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import stomp
import time
import socket

USERNAME = 'NROD_USERNAME'
PASSWORD = 'NROD_PASSWORD'
HOSTNAME = 'datafeeds.networkrail.co.uk'
HOSTPORT = 61618
# Always prefixed by /topic/ (it's not a queue, it's a topic)
TOPIC='/topic/TD_LNE_GN_SIG_AREA'

CLIENT_ID = socket.getfqdn()
HEARTBEAT_INTERVAL_MS = 15000
RECONNECT_DELAY_SECS = 15

if USERNAME == '':
    raise Exception("Please configure your username and password in opendata-nationalrail-client.py!")


def connect_and_subscribe(connection):
    connection.start()

    connect_header = {'client-id': USERNAME + '-' + CLIENT_ID}
    subscribe_header = {'activemq.subscriptionName': CLIENT_ID}

    connection.connect(username=USERNAME,
                       passcode=PASSWORD,
                       wait=True,
                       headers=connect_header)

    connection.subscribe(destination=TOPIC,
                         id='1',
                         ack='auto',
                         headers=subscribe_header)


class StompClient(stomp.ConnectionListener):

    def on_heartbeat(self):
        print('Received a heartbeat')

    def on_heartbeat_timeout(self):
        print('ERROR: Heartbeat timeout')

    def on_error(self, headers, message):
        print('ERROR: %s' % message)

    def on_disconnected(self):
        print('Disconnected waiting %s seconds before exiting' % RECONNECT_DELAY_SECS)
        time.sleep(RECONNECT_DELAY_SECS)
        exit(-1)

    def on_connecting(self, host_and_port):
        print('Connecting to ' + host_and_port[0])

    def on_message(self, headers, message):
        try:
            print('\n---\nGot message %s' % message)
        except Exception as e:
            print("\n\tError: %s\n--------\n" % str(e))


conn = stomp.Connection12([(HOSTNAME, HOSTPORT)],
                          auto_decode=False,
                          heartbeats=(HEARTBEAT_INTERVAL_MS, HEARTBEAT_INTERVAL_MS))

conn.set_listener('', StompClient())
connect_and_subscribe(conn)

while True:
    time.sleep(1)

conn.disconnect()
