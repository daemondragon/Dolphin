#! /bin/sh

# Script to regenerate all datasets at once (in correct order)
# All scripts that generate datasets must be added to this list at the correct place

echo "assets"
python3 assets.py
echo "rate"
python3 rate.py

echo "volatility"
python3 volatility.py
echo "sharpe"
python3 sharpe.py

echo "correlation"
python3 correlation.py
echo "covariance"
python3 covariance.py

echo "rendement"
python3 rendement.py
echo "rendement_A"
python3 rendement_A.py