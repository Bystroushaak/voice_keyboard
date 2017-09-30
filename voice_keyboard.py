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


BS = "\x08"
ESC = "\x1b"


def _make_connection(server, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))

    return client


def _verbose_wrapper_make_connection(server, port):
    """
    Try to make connection to given server:port. If the connection can't be
    established, wait and try again after one second.
    """
    while True:
        try:
            conn = _make_connection(server, port)
            print "Connected"
            return conn
        except socket.error:
            sys.stderr.write("Can't connect to %s:%d " % (server, port))
            sys.stderr.write("Waiting 1s..\n")
            time.sleep(1)


def read_from(server, port):
    readers = []

    def reset_connection():
        while readers:
            readers.pop()

        readers.append(_verbose_wrapper_make_connection(server, port))

    reset_connection()

    last_time = 0
    while True:
        read_ready, _, errors = select.select(readers, [], [], 5)

        if errors:
            for error in errors:
                error.close()

            reset_connection()
            continue

        if time.time() - last_time < 0.5:
            continue

        for s in read_ready:
            try:
                data = s.recv(1024)
            except socket.error:
                yield ESC
                reset_connection()
                break

            if data:
                yield data
            else:
                yield ESC
                # restart connection
                reset_connection()

        last_time = time.time()


class TextProcessor(object):
    def __init__(self):
        self.sent = ""

    def reset(self):
        self.sent = ""

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

    def _no_bs_at_start(self, line):
        cnt = 0
        for i in line:
            if i == BS:
                cnt += 1
            else:
                break

        return cnt

    def process_text(self, data):
        data = data.strip()

        if not data:
            return

        if not data.replace(BS, "").strip():
            return

        # new line
        if ESC in data:
            self.reset()
            return

        bs_cnt = self._no_bs_at_start(data)

        buffer = [x for x in data[bs_cnt:].split(BS) if x.strip()][-1]

        # because of the only delta of the sentence is sent, I want to work
        # with unicode to prevent splitting UTF-8 sequences
        buffer = buffer.decode("utf-8", "ignore")

        buffer = buffer.replace(" enter ", "\n")
        buffer = buffer.replace(" Enter ", "\n")
        # buffer = buffer.replace("enter ", "\n")
        # buffer = buffer.replace("Enter ", "\n")
        buffer = buffer.replace("enter", "\n")
        buffer = buffer.replace("Enter", "\n")

        buffer = buffer.replace(BS, "[BS]")

        print
        print ">s>%s<<<" % buffer

        self.send_diff(buffer)

    def _index_where_differ(self, a, b):
        """
        Just simple comparator to see the index where the a and b are
        different.
        """
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

    def send_diff(self, buffer):
        if not self.sent:
            self.send(buffer)
            self.sent = buffer
            return

        # apple's voice recognition tends to correct sentences as you type
        # this tries to compare the sentence with the already sent data, to
        # see what was chenged and then send only difference of the change
        di = self._index_where_differ(self.sent, buffer)

        # do not go more than 5 characters to the past (using backspace)
        if len(self.sent) - di > 5:
            di = len(self.sent) - 5

        def nothing_changed(di):
            return di == len(self.sent)

        if nothing_changed(di):
            if len(buffer) > di:
                new = buffer[di:]
                self.send(new)
                self.sent += new
        else:
            tail = self.sent[di:]
            self.sent = self.sent[:di]

            for _ in tail:
                self.backspace()

            new = buffer[di:]
            self.send(new)
            self.sent += new


if __name__ == '__main__':
    text_processor = TextProcessor()
    for chunk in read_from(sys.argv[1], int(sys.argv[2])):
        text_processor.process_text(chunk)
