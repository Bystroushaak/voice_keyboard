#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
import os
import sys
import time
import select
import socket


def _make_connection(server, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))

    return client


def connect_to(server, port, callback):
    readers = [_make_connection(server, port)]

    last_time = 0
    while True:
        read_ready, _, errors = select.select(readers, [], [], 5)

        if errors:
            for error in errors:
                error.close()

            readers = [_make_connection(server, port)]

            continue

        if time.time() - last_time < 0.5:
            continue

        for s in read_ready:
            data = s.recv(1024)
            if data:
                callback(data)

        last_time = time.time()


class TemporaryBuffer(object):
    def __init__(self):
        self.storage = ""
        self.sent = ""

    def reset(self):
        self.storage = ""
        self.sent = ""

    def _no_bs_at_start(self, line):
        cnt = 0
        for i in line:
            if i == "":
                cnt += 1
            else:
                break

        return cnt

    def process(self, data):
        data = data.strip()

        if not data:
            return

        if not data.replace("", "").strip():
            return

        # new line
        if "" in data:
            self.reset()
            return

        bs_cnt = self._no_bs_at_start(data)

        storage = [x for x in data[bs_cnt:].split("") if x.strip()][-1]

        data = data.replace("", "[ESC]")
        data = data.replace("", "[BS]")

        print
        print ">s>%s<<<" % storage

        storage = storage.decode("utf-8", "ignore")

        storage = storage.replace(" enter ", "\n")
        storage = storage.replace(" Enter ", "\n")
        # storage = storage.replace("enter ", "\n")
        # storage = storage.replace("Enter ", "\n")
        storage = storage.replace("enter", "\n")
        storage = storage.replace("Enter", "\n")

        self.send_diff(storage)

    def send(self, data):
        data = data.encode("utf-8")
        lines = data.split("\n")

        if len(lines) == 1:
            print "send>%s" % data
            os.system("xdotool type '{}'".format(data))
            return

        head = lines[:-1]
        tail = lines[-1]

        for line in head:
            print "send>%s\\n" % data
            os.system("xdotool type '{}'".format(line))
            os.system("xdotool key Return")

        os.system("xdotool type '{}'".format(tail))

    def backspace(self):
        os.system("xdotool key BackSpace")
        print "send>backspace"

    def _index_where_differ(self, a, b):
        if not a:
            return 0

        if not b:
            return 0

        for i in range(len(a)):
            if i >= len(b):
                return i

            if a[i] != b[i]:
                return i

        return len(a)

    def send_diff(self, storage):
        if not self.sent:
            self.send(storage)
            self.sent = storage
            return

        di = self._index_where_differ(self.sent, storage)

        if di == len(self.sent):
            if len(storage) > di:
                new = storage[di:]
                self.send(new)
                self.sent += new
        else:
            tail = self.sent[di:]
            self.sent = self.sent[:di]

            for _ in tail:
                self.backspace()

            new = storage[di:]
            self.send(new)
            self.sent += new



if __name__ == '__main__':
    buffer = TemporaryBuffer()
    connect_to(sys.argv[1], int(sys.argv[2]), buffer.process)
a