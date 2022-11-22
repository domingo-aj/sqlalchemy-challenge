import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Datebase Setup
dateback = dt.date(2017, 8, 23) - dt.timedelta(days=365)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement

station = Base.classes.station

app = Flask(__name__)

#Flask route building
@app.route("/")
def homepage():
    return (
        f"Routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start=YYYY-MM-DD</br>"
        f"/api/v1.0/start=YYYY-MM-DD/end=YYYY-MM-DD</br>"
    )

#def routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= dateback).\
        order_by(measurement.date.desc()).all()

    session.close()

    pobs = []
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['precipitation'] = prcp
        pobs.append(prcp_dict)

    return jsonify(pobs)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station).all()

    stations= []
    for result in results: 
        station_dict = {}
        station_dict["id"] = result.id
        station_dict["name"] = result.name
        station_dict["latitude"] = result.latitude
        station_dict["longitude"] = result.longitude
        station_dict["elevation"] = result.elevation
        stations.append(station_dict)

    session.close( )

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    station = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()
    
    active_station = station.station

    results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= dateback).\
    filter(measurement.station == active_station).\
    order_by(measurement.date.desc()).all()

    session.close()

    tobs_data = []
    for date, tobs in results: 
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs 
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/start=<start>")
def start_date(start): 
    session = Session(engine)

    results = session.query(func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()

    session.close()

    tobs_data = []
    for tmin, tmax, tavg in results: 
        tobs_dict = {}
        tobs_dict["Temp Min"] = tmin
        tobs_dict["Temp Max"] = tmax 
        tobs_dict["Temp Avg"] = tavg
        tobs_data.append(tobs_dict)

        return jsonify(tobs_data)

@app.route("/api/v1.0/start=<start>/end=<end>")
def dates(start, end): 
    session = Session(engine)

    results = session.query(func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    
    session.close()

    tobs_data = []
    for tmin, tmax, tavg in results: 
        tobs_dict = {}
        tobs_dict["Temp Min"] = tmin
        tobs_dict["Temp Max"] = tmax 
        tobs_dict["Temp Avg"] = tavg
        tobs_data.append(tobs_dict)

        return jsonify(tobs_data)

if __name__ == '__main__':
    app.run(debug=True)