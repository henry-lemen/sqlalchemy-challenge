# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurements = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(func.max(Measurements.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = latest_date - dt.timedelta(days=365)
    query = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date > one_year_ago).filter(Measurements.station == 'USC00519281')
    prcp_results = {}
    for date, prcp in query.all():
        prcp_results[date] = prcp
    return jsonify(prcp_results)
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(station_results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest_date = session.query(func.max(Measurements.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = latest_date - dt.timedelta(days=365)
    most_active_results = session.query(Measurements.tobs).filter(Measurements.date > one_year_ago).filter(Measurements.station == 'USC00519281')
    session.close()
    most_active = list(np.ravel(most_active_results))
    return jsonify(most_active)

@app.route("/api/v1.0/<start>")
def start(start):
    query = session.query(
        func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)
    ).filter(Measurements.date >= start).all()

    result_start = {
            'start_date': start,
            'tmin': query[0][0],
            'tavg': query[0][1],
            'tmax': query[0][2]
        }
    return jsonify(result_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Incorrect date format, should be YYYY-MM-DD"}), 400
    query = session.query(
        func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)
    ).filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
    if query[0][0] is None:
        return jsonify({"error": "No temperature data found for the given date range."}), 404
    result_startend = {
        'start_date': start,
        'end_date': end,
        'tmin': query[0][0],
        'tavg': query[0][1],
        'tmax': query[0][2]
    }
    return jsonify(result_startend)