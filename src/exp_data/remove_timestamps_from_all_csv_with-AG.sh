#!/bin/bash

for x in *-AG*.csv; do mv "$x" "${x/-AG*}-AG.csv"; done