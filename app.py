import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)

app = Flask(__name__)


@app.route("/")
def helloWorld():
    # urls that tell the user the end points that are available
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
        
    )

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
   ## return a list of all the stations in JSON Format
    listOfStations = session.query(Station.station).all()
    stationOneDimension = list(np.ravel(listOfStations))
    return jsonify(stationOneDimension=stationOneDimension)



@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    station_number = "USC00519281"
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    outcome = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= prev_year).all()
    temps = {}
    for row in outcome:
        temps[row[0]]=row[1]
    temps = list(np.ravel(temps))
    return jsonify(temps=temps)


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    prcp_database = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    precip = {}
    for row in prcp_database:
        precip[row[0]]=row[1]
    return jsonify(precip)


@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps(start, end):
   
    session = Session(engine)

    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    query = query.filter(Measurement.date >= start)

    if end is not None:
        query = query.filter(Measurement.date <= end)
    
    results = query.all()

    (tmin, tavg, tmax) = results[0]

    session.close()

    return jsonify({'temp_min' : tmin, 'temp_avg' : tavg, 'temp_max' : tmax})
    
if __name__ == '__main__':
    app.run()