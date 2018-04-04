# -*- coding: utf-8 -*-
import mmap


def get_line_number(file_path):
    fp = open(file_path, "r")
    buf = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
    lines = 0
    while buf.readline():
        lines += 1
    return lines
