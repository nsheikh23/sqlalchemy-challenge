# Dependencies
import numpy as np
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start_date&gt;<br/>"
        f"/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    final = list(np.ravel(results))

    return jsonify(final)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for Stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    final = list(np.ravel(results))

    return jsonify(final)

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

    temp = (session.query(Measurement.date, Measurement.tobs)
            .filter(Measurement.station == most_active_station)
            .filter(Measurement.date >='2016-08-23')
            .all()
            )

    session.close()

    # Convert list of tuples into normal list
    final = list(np.ravel(temp))

    return jsonify(final)


@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create our session from Python to the DB
    session = Session(engine)

    # Query for all dates starting with entered date
    tmin = (session.query(func.min(Measurement.tobs))
            .filter(Measurement.date >= start)
            .all()
            )
    
    tmax = (session.query(func.max(Measurement.tobs))
            .filter(Measurement.date >= start)
            .all()
            )

    tavg = (session.query(func.avg(Measurement.tobs))
            .filter(Measurement.date >= start)
            .all()
            )

    session.close()

    results = tuple(tmin,tavg,tmax)
    # Convert list of tuples into normal list
    final = list(np.ravel(results))

    return jsonify(final)





if __name__ == '__main__':
    app.run(debug=True)