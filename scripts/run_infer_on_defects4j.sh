#!/bin/bash

echo ">>> Running Infer" && python3 python/RunInfer.py \
    -dataset /vul4j/dataset/vul4j_dataset.csv \
    -infer ../static-checkers/infer-linux64-v1.1.0/bin/infer \
    -github github.json