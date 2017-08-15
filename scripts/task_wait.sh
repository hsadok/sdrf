#!/bin/bash
args=("$@")

awk -F',' '{ $1 = $2 - $1 } 1' ${args[0]} | cut -f1 -d" "
