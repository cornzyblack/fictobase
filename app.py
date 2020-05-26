import json
from flask import Flask, render_template, request, render_template
from random import randint
from utils import (
    get_org_info,
    extract_details_json,
    extract_date_pair,
    get_total_funding,
    employee_generator,
    random_fund_generator,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def get_about():
    return render_template("about.html")


@app.route("/company", methods=["GET"])
def get_company():
    company_name = request.args.get("company_name")
    company_details_json = get_org_info(company_name).json()
    data = extract_details_json(company_details_json)

    # with open("sample.json", "r") as company_details_json:
    #     data = extract_details_json(json.loads(company_details_json.read()))

    total_funding, total_funding_dict = random_fund_generator(company_name)
    total_employees, total_employee_dict = employee_generator(company_name)

    data.update({"total_employees": total_employees})
    data.update({"total_employee_dict": total_employee_dict})
    data.update({"total_funding": total_funding})
    data.update({"total_funding_dict": total_funding_dict})

    print(data)
    return render_template("company.html", data=data)
