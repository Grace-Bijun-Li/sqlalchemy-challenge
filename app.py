# Import everything you used in the starter_climate_analysis.ipynb file, along with Flask modules
import numpy as np
import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Create an engine
engine = create_engine("sqlite:///data/hawaii.sqlite")

# reflect an existing database into a new model with automap_base() and Base.prepare()
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Instantiate a Session and bind it to the engine
# session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
# Instantiate a Flask object at __name__, and save it to a variable called app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Set the app.route() decorator for the base '/'
# define a welcome() function that returns a multiline string message to anyone who visits the route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/&lt;start&gt;<br/>"
        f"/api/v1.0/temp/&lt;start&gt;/&lt;end&gt;"
    )

# Set the app.route() decorator for the "/api/v1.0/precipitation" route
# define a precipitation() function that returns jsonified precipitation data from the database
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(bind=engine)
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
    # Calculate the date 1 year ago from last date in database
    last_year_date = datetime.date(2017,8,23) - datetime.timedelta(days=365)
    # Query for the date and precipitation for the last year
    date_prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date>=last_year_date).all()
    # Create a dictionary to store the date: prcp pairs. 
    # Hint: check out a dictionary comprehension, which is similar to a list comprehension but allows you to create dictionaries
    date_prcp_list = []
    
    for date, prcp in date_prcp_data:
        date_prcp_dict = {}
        date_prcp_dict['date'] = date
        date_prcp_dict['prcp'] = prcp
        date_prcp_list.append(date_prcp_dict)
    
    session.close()
    # Return the jsonify() representation of the dictionary
    return jsonify(date_prcp_list)


# Set the app.route() decorator for the "/api/v1.0/stations" route
# define a stations() function that returns jsonified station data from the database
@app.route("/api/v1.0/stations")
def stations():
    session = Session(bind=engine)
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
    # Query for the list of stations
    station_list = session.query(measurement.station).distinct()
    # Unravel results into a 1D array and convert to a list
    # Hint: checkout the np.ravel() function to make it easier to convert to a list
    all_stations = [station[0] for station in station_list]
    session.close()
    # Return the jsonify() representation of the list
    return jsonify(all_stations)

# Set the app.route() decorator for the "/api/v1.0/tobs" route
# define a temp_monthly() function that returns jsonified temperature observations (tobs) data from the database
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(bind=engine)
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
    # Calculate the date 1 year ago from last date in database
    last_year_date = datetime.date(2017,8,23) - datetime.timedelta(days=365)
    # Query the dates and temperature observations of the most active station for the last year of data
    active_station_temp = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date>=last_year_date).order_by(measurement.date).all()
    # Unravel results into a 1D array and convert to a list
    # Hint: checkout the np.ravel() function to make it easier to convert to a list
    active_station_temp_list = [temp[0] for temp in active_station_temp]
    session.close()
    # Return the jsonify() representation of the list
    return jsonify(active_station_temp_list)

# Set the app.route() decorator for the "/api/v1.0/temp/<start>" route and "/api/v1.0/temp/<start>/<end>" route
# define a stats() function that takes a start and end argument, and returns jsonified TMIN, TAVG, TMAX data from the database
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps(start, end=None):
    print(start,end)
    session = Session(bind=engine)
    if end is None:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        temp_list = []

        results = (session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
                          .filter(measurement.date >= start)
                          .group_by(measurement.date)
                          .all())
        print(results)
        # Unravel results into a 1D array and convert to a list
        # Hint: checkout the np.ravel() function to make it easier to convert to a list
        for date, min, avg, max in results:
            temp_dict = {}
            temp_dict["Date"] = date
            temp_dict["TMIN"] = min
            temp_dict["TAVG"] = avg
            temp_dict["TMAX"] = max
            temp_list.append(temp_dict)
 
        # Return the jsonify() representation of the list
        return jsonify(temp_list)

    else:
        # calculate TMIN, TAVG, TMAX with both start and stop
        temp_list_2 = []

        results_2 = (session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
                            .filter(measurement.date>=start)
                            .filter(measurement.date<=end)
                            .group_by(measurement.date)
                            .all())
        # Unravel results into a 1D array and convert to a list
        # Hint: checkout the np.ravel() function to make it easier to convert to a list
        for date, min, avg, max in results_2:
            temp_dict_2 = {}
            temp_dict_2["Date"] = date
            temp_dict_2["TMIN"] = min
            temp_dict_2["TAVG"] = avg
            temp_dict_2["TMAX"] = max
            temp_list_2.append(temp_dict_2)

        session.close()
        # Return the jsonify() representation of the list
        return jsonify(temp_list_2)
    
if __name__ == '__main__':
    app.run()
