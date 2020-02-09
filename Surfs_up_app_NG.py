import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
# ---------------------------------------------------
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
last_date = (session.query(Measurement.date).\
             order_by(Measurement.date.desc()).first())
    # Calculate the date 1 year ago from the last data point in the database
last_date = list(np.ravel(last_date))[0]
    #turn object into string
last_dt = dt.datetime.strptime(last_date, '%Y-%m-%d')
    #turn string into datetime format
last_year = int(dt.datetime.strftime(last_dt, '%Y'))
    #pull year out of dt date
last_month = int(dt.datetime.strftime(last_dt, '%m'))
    #pull month out of dt date
last_day = int(dt.datetime.strftime(last_dt, '%d'))
    #pull day out of dt date
first_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)

app = Flask(__name__)

hello_dict = {"Hello": "World!"}


@app.route("/")
def home():
    return (f"Welcome to the Hawaii Climate API - Surfs Up!</br>"
            f"</br>"
            f"Sections:</br>"
            f"/api/v1.0/precipitation </br>"
            f"/api/v1.0/stations </br>"
            f"/api/v1.0/tobs </br>"
            f"<br/>"
            f"datesearch (yyyy-mm-dd) <br/>"
            f"/api/v1.0/datesearch/2016-08-23  ~~~~~~~~~~~ low, high, and average temp for date given and each date after <br/>"
            f"/api/v1.0/datesearch/2016-08-23/2017-08-23 ~~ low, high, and average temp for date given and each date up to and including end date <br/>"
            f"<br/>"
            f"data available from 2010-01-01 to 2017-08-23 <br/>")




@app.route("/api/v1.0/precipitation")
def precipitation():
    prec_scores = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
    filter(Measurement.date > first_date).\
    order_by(Measurement.date).all()

    prec_data = []
    for prec_score in prec_scores:
        prec_dict = {prec_score.date: prec_score.prcp, 
                    "Station": prec_score.station}
        prec_data.append(prec_dict)

    return jsonify(prec_data)

@app.route("/api/v1.0/stations")
def stations():
    Station_list = (session.query(Station.name).all())
    Station_list = list(np.ravel(Station_list))
    return jsonify(Station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_scores = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
    filter(Measurement.date > first_date).\
    order_by(Measurement.date).all()

    temp_data = []
    for tobs_score in tobs_scores:
        temp_dict = {tobs_score.date: tobs_score.tobs, "Station": tobs_score.station}
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route('/api/v1.0/datesearch/2016-08-23')
def start():
    start_info = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start_dates =  (session.query(*start_info)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= first_date)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for start_date in start_dates:
        date_dict = {}
        date_dict["Date"] = start_date[0]
        date_dict["Low Temp"] = start_date[1]
        date_dict["Avg Temp"] = start_date[2]
        date_dict["High Temp"] = start_date[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/2016-08-23/2017-08-23')
def startEnd():
    date_info = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start_end_dates =  (session.query(*date_info)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= first_date)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= last_date)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for start_end_date in start_end_dates:
        date_dict = {}
        date_dict["Date"] = start_end_date[0]
        date_dict["Low Temp"] = start_end_date[1]
        date_dict["Avg Temp"] = start_end_date[2]
        date_dict["High Temp"] = start_end_date[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)
