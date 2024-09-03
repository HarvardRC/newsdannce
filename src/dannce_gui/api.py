import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    make_response,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, init_db, JOB_TABLE

from .logic.make_training_dir import make_training_dir
from .logic.submit_job import submit_job
from .logic.sbatch_builders import make_sbatch_str
from .logic.sdannce_command_enum import SDannceCommand

bp_api = Blueprint(
    "api",
    __name__,
    static_folder="static",
    template_folder="templates",
    url_prefix="/api",
)


@bp_api.get("/status")
def get_status_route():
    return make_response({"status": "ok"}, 200)


@bp_api.post("/create-training-dir")
def create_training_dir_route():
    data = request.json
    com_exp_list = data["com_exp_list"]
    dannce_exp_list = data["dannce_exp_list"]
    project_folder = data["project_folder"]

    base_dir_final = make_training_dir(
        base_dir=project_folder,
        delete_if_exists=True,
        com_exp_list=com_exp_list,
        dannce_exp_list=dannce_exp_list,
    )

    return make_response({"project_folder": base_dir_final}, 200)


@bp_api.post("/submit-job")
def submit_job_route():
    data = request.json
    config_path = data["config_path"]
    project_folder = data["project_folder"]
    command = data["command"]

    try:
        command_enum = SDannceCommand(command)
    except Exception as e:
        return make_response({"error": "command is invalid"}, 400)

    sbatch_str = make_sbatch_str(
        command_enum, project_folder=project_folder, config_path=config_path
    )

    # return sbatch_str
    job_id = submit_job(sbatch_str, command_enum, project_folder)

    return make_response({"job_id": job_id})


@bp_api.post("/update-job-status-all")
def update_job_statuses_route():
    data = request.json

    # submit_job.
    return make_response({"job_id": -1})  # TODO: contnue dev


# @bp_api.post("completed-job-info")
# def completed_job_info_route():
#     data = request.json
#     job_id = data["job_id"]

# query job info


@bp_api.post("init-db")
def init_db_route():
    init_db()
    return "Ok"


@bp_api.get("list-jobs")
def list_jobs_route():
    conn = get_db()
    result = conn.execute(f"SELECT * FROM {JOB_TABLE} ORDER BY created_at").fetchall()

    result_dict = [dict(x) for x in result]
    return make_response({"data": result_dict}, 200)
