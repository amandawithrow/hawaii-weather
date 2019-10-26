import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#DATABASE SETUP
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# FLASK SETUP
app = Flask(__name__)

# FLASK ROUTES

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Hawaii Climate Analysis API"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list precipitation by date"""
    #calculate query date
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    #query for date and precipitation
    rain = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date).all()
    
    #create dict - date as key, prcp as value - using list comprehension
    pre = {date: prcp for date, prcp in rain}
    return jsonify(pre)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query to get list of stations
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations)
    
@app.route("/api/v1.0/tobs")
def temperatures():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.date>=query_date).\
        filter(Measurement.station == "USC00519281").all()
    temperature = list(np.ravel(results))
    return jsonify(temperature)
    
    
@app.route("/api/v1.0/temp/<start>")
def starting(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start"""
    stats = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*stats).filter(Measurement.date>=start).all()
    temp_dict = list(np.ravel(results))
    return jsonify(temp_dict)

@app.route("/api/v1.0/temp/<start>/<end>")
def ranges(start = None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given date range"""
    stats = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*stats).filter(Measurement.date>=start).\
             filter(Measurement.date <= end).all()
    temp_dict = list(np.ravel(results))
    return jsonify(temp_dict)
   

if __name__ == '__main__':
    app.run()
