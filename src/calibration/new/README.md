# New Calibration (WIP)

New calibration for `newsdannce` repo

Idea: single canonical calibration pipeline

Goals:
- remove dependency on Matlab
- robust, accurate calibration
- easy to set up
- well documented 

How to run pytest:

python -m pytest src/calibration/new

Example usage:

```
python -m src.calibration.new.calibrate -p "~/olveczky/dannce_data/setupCal11_010324" -r 6 -c 9 -s 23 -o "~/olveczky/dannce_data/setupCal11_010324/calibration_export"
```
