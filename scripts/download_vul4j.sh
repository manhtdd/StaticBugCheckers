#!/bin/bash

echo ">>> Checking out the dataset"

# Run a Python script to check out buggy versions using Defects4J
python3 python/CheckoutV4j.py \
    -dataset /vul4j/dataset/vul4j_dataset.csv
