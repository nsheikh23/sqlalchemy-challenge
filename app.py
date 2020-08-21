# Dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources\hawaii.sqlite")

# Reflect an existing DB into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def HomePage ():
    """List all available api routes."""
    return(
        f"Available Routes are: <br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation data</a><br/>"
        f"<a href='/api/v1.0/stations'>List of all the stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>Last year's temperature for the most active station</a><br/>"
        f"Temperature statistics since a specified date: <a href='/api/v1.0/2016-01-01'>/api/v1.0/&lt;start_date&gt;</a><br/>"
        f"Temperature statistics between date range: <a href='/api/v1.0/2016-01-01/2016-01-15'>/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;</a><br/>"
        f"<br/>"
        f"*For dates, please use the format: (eg. 2016-01-01) <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precip_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Precipitation'] = prcp
        precip_list.append(prcp_dict)

    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for Stations
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()

    session.close()

    stations = []
    for station,name,lat,lng,elv in results:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_dict['Lat'] = lat
        station_dict['Lng'] = lng
        station_dict['Elevation'] = elv
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for most active station
    most_active_station = (session.query(Measurement.station, func.count(Measurement.station))
                  .group_by(Measurement.station)
                  .order_by(func.count(Measurement.station).desc())
                  .all()
                 )[0][0]

    last_str_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())[0]
    date_conversion = dt.datetime.strptime(last_str_date, '%Y-%m-%d')
    last_yr = dt.date(date_conversion.year -1, date_conversion.month, date_conversion.day)

    temp = (session.query(Measurement.date, Measurement.tobs)
            .filter(Measurement.station == most_active_station)
            .filter(Measurement.date >= last_yr)
            .all()
            )

    session.close()

    tempsall = []
    for date,tobs in temp:
        temps_dict = {}
        temps_dict['Date'] = date
        temps_dict['Temperature'] = tobs
        tempsall.append(temps_dict)

    return jsonify(tempsall)


@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for all dates starting with entered date
    temp_stats = (session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs)), func.max(Measurement.tobs))
            .filter(Measurement.date >= start)
            .all()
            )

    session.close()

    temps_all = []
    for min,avg,max in temp_stats:
        temps_dict = {}
        temps_dict["Min"] = min
        temps_dict["Avg"] = avg
        temps_dict["Max"] = max
        temps_all.append(temps_dict)

    return jsonify(temps_all)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for all dates starting with entered date
    temp_stats = (session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs)), func.max(Measurement.tobs))
            .filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
            )

    session.close()

    temps_all = []
    for min,avg,max in temp_stats:
        temps_dict = {}
        temps_dict["Min"] = min
        temps_dict["Avg"] = avg
        temps_dict["Max"] = max
        temps_all.append(temps_dict)

    return jsonify(temps_all)

if __name__ == '__main__':
    app.run(debug=True)