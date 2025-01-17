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
engine = create_engine("sqlite:///hawaii.sqlite")

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
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year = dt.datetime(2016, 8, 23)
    query = session.query(Measurements.prcp).filter(Measurements.date > one_year).filter(Measurements.station == 'USC00519281')
    prcp_results = {}
    for x in query.all():
        prcp_results[date.strftime('%Y-%m-%d')] = prcp
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
    one_year = dt.datetime(2016, 8, 23)
    most_active_results = session.query(Measurements.tobs).filter(Measurements.date > one_year).filter(Measurements.station == 'USC00519281')
    session.close()
    most_active = list(np.ravel(most_active_results))
    return jsonify(most_active)

@app.route("/api/v1.0/<start>")
def start():
    start_date = dt.datetime(2017, 8, 23)
    query = session.query(
        func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)
    ).filter(Measurements.date >= start_date)
    result = query.all()
    return jsonify({
            'start_date': start_date,
            'tmin': result.tmin,
            'tavg': result.tavg,
            'tmax': result.tmax
        })

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    start_date = dt.datetime(2017, 8, 23)
    end_date = dt.datetime(2017,1,1)
    query = session.query(
        func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)
    ).filter(Measurements.date >= start_date).filter(Measurements.date < end_date)
    result = query.all()
    return jsonify({
            'start_date': start_date,
            'tmin': result.tmin,
            'tavg': result.tavg,
            'tmax': result.tmax
        })