from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)

# Database setup
engine = create_engine("sqlite:////Users/laurenpescarus/Desktop/MSU Course/Classwork/sqlalchemy-challenge/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Home route with explicit url parameters
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; (e.g., /api/v1.0/2017-01-01)<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; (e.g., /api/v1.0/2017-01-01/2017-12-31)<br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date one year from the last date in data set.
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_data_date = dt.datetime.strptime(last_data_point.date, '%Y-%m-%d')
    one_year_before_last_data = last_data_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_before_last_data).\
              filter(Measurement.date <= last_data_date).all()
    session.close()

    # Convert list of tuples into normal list
    precipitation_dict = {date: prcp for date, prcp in results if prcp is not None}
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))
    return jsonify(station_list)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Determine the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).\
        first().station

    # Calculate the date one year from the last date in data set.
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_data_date = dt.datetime.strptime(last_data_point.date, '%Y-%m-%d')
    one_year_before_last_data = last_data_date - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_before_last_data).\
        filter(Measurement.date <= last_data_date).all()
    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

# Start route
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    # Create a dictionary for min/max/avg
    temp_stats = list(np.ravel(results))
    return jsonify(temp_stats)

# Start/End route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).all()
    session.close()

    # Create a dictionary for min/max/avg
    temp_stats = list(np.ravel(results))
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
