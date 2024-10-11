module load Mambaforge
conda run -n dannce-dev --no-capture-output python -m fastapi dev ./app/main.py --host 0.0.0.0
