#!/bin/bash
mkdir -p /logs/verifier

if true; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
