#!/bin/bash
export PYTHONPATH=.
export FMP_API_KEY="${FMP_API_KEY:-test}"
python -m unittest discover tests