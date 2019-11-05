from flask import Flask, request, jsonify, render_template
from database import db, db_init
from models import Air
from sqlalchemy.sql import func
import pandas as pd
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def main():
    return render_template('index.html')

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

@app.route('/poly')
def poly():
    res = []
    for name in os.listdir('static/data/'):
        path = 'static/data/' + name
        with open(path) as f:
            res.append(json.load(f))
    return jsonify(res)

@app.route('/range', methods=['POST'])
def trange():
        t = int(request.form['time'])*100
        resv = db.session.query(Air.Station, Air.Id, func.avg(Air.CarbonMonoxide).label("CarbonMonoxide"),
                                func.avg(Air.Ozone).label("Ozone"),
                                func.avg(Air.NitrogenDioxide).label("NitrogenDioxide"),
                                func.avg(Air.SulfurDioxide).label("SulfurDioxide"), func.avg(Air.PM25).label("PM25"),
                                func.avg(Air.PM10).label("PM10"),
                                func.avg(Air.VisibilityReduction).label("VisibilityReduction"),
                                func.avg(Air.AQI).label("AQI"), func.avg(Air.Summary).label("Summary")).filter(
            Air.Time >= t, Air.Time<t+24).group_by(Air.Station, Air.Id)

        res = [dict(zip(result.keys(), result)) for result in resv.all()]
        return jsonify(res)

@app.route('/mapchart', methods=['POST'])
def mapchart():
        t = int(request.form['date'])*100
        stationid = int(request.form['id'])
        resv = db.session.query(Air.Time, Air.PM25).filter(
            Air.Time >= t, Air.Time<t+24, Air.Id == stationid)

        res = [dict(zip(result.keys(), result)) for result in resv.all()]
        return jsonify(res)

@app.route('/chart1', methods=['POST'])
def chart1():
    def getaqi(raw_d):
        res = [0 for i in range(24)]
        res_count = [0 for i in range(24)]
        for d in raw_d:
            if d['AQI'] == None:
                continue
            res[d['Time']%100] += d['AQI']
            res_count[d['Time'] % 100] += 1
        for idx, v in enumerate(res):
            if res_count[idx] !=0:
                res[idx] /= res_count[idx]
        relres = [{'timeid':i, 'aqi':v} for i, v in enumerate(res)]
        return relres
    station = int(request.form['station'])
    res = {}
    res['2015'] =getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.AQI).filter(Air.Id==station, Air.Time>=2015010100, Air.Time<2016010100).all()])
    res['2016'] =getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.AQI).filter(Air.Id==station, Air.Time>=2016010100, Air.Time<2017010100).all()])
    res['2017'] =getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.AQI).filter(Air.Id==station, Air.Time>=2017010100, Air.Time<2018010100).all()])
    res['2018'] =getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.AQI).filter(Air.Id==station, Air.Time>=2018010100, Air.Time<2019010100).all()])
    res['2019'] =getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.AQI).filter(Air.Id==station, Air.Time>=2019010100, Air.Time<2020010100).all()])
    return jsonify(res)

@app.route('/chart2', methods=['POST'])
def chart2():
    time = int(request.form['time'])
    res = [dict(zip(result.keys(), result)) for result in db.session.query(Air.Id.label('id'), func.avg(Air.AQI).label('aqi'), func.max(Air.AQI).label('max')).filter(Air.Time%100==time).group_by(Air.Station).all()]
    for one in res:
        maxdate = [dict(zip(result.keys(), result)) for result in db.session.query(Air.Time).filter(Air.Time%100==time, Air.Id==one['id'], Air.AQI == one['max']).all()]
        one['Time'] = maxdate[0]['Time']
    return jsonify(res)

@app.route('/chart3', methods=['POST'])
def chart3():
    def getpm25(data):
        res = [0 for i in range(12)]
        res_count = [0 for i in range(12)]
        maxcount = [0 for i in range(12)]
        maxdate = [0 for i in range(12)]
        for one in data:
            month = int(one['Time']/10000)%100-1
            if one['PM25'] is not None:
                res[month] += one['PM25']
                res_count[month] += 1
                if one['PM25'] > maxcount[month]:
                    maxcount[month] = one['PM25']
                    maxdate[month] = one['Time']
        for i in range(12):
            if res_count[i] != 0:
                res[i] /= res_count[i]
        trueres = []
        for i, v in enumerate(res):
            trueres.append({
                'Month':i+1,
                'PM25':v,
                'Time':maxdate[i],
                'Max':maxcount[i]
            })
        return trueres
    station = int(request.form['station'])
    year = int(request.form['year'])
    res = getpm25([dict(zip(result.keys(), result)) for result in db.session.query(Air.PM25, Air.Time).filter(Air.Id==station, Air.Time>=year*1000000, Air.Time<(year+1)*1000000).all()])
    return jsonify(res)

@app.route('/chart4', methods=['POST'])
def chart4():
    def getaqi(raw_d, key):
        res = [0 for i in range(24)]
        res_count = [0 for i in range(24)]
        for d in raw_d:
            if d[key] == None:
                continue
            res[d['Time']%100] += d[key]
            res_count[d['Time'] % 100] += 1
        for idx, v in enumerate(res):
            if res_count[idx] !=0:
                res[idx] /= res_count[idx]
        relres = [{'timeid':i, key:v} for i, v in enumerate(res)]
        return relres
    station = int(request.form['station'])
    year = int(request.form['year'])
    res = []
    res.append(getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, (Air.CarbonMonoxide*50).label('CarbonMonoxide')).filter(Air.Id==station, Air.Time/1000000-year>=0, Air.Time/1000000-year<1).all()], 'CarbonMonoxide'))
    res.append(getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.Ozone).filter(Air.Id==station, Air.Time/1000000-year>=0, Air.Time/1000000-year<1).all()], 'Ozone'))
    res.append(getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.NitrogenDioxide).filter(Air.Id==station, Air.Time/1000000-year>=0, Air.Time/1000000-year<1).all()], 'NitrogenDioxide'))
    res.append(getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, (Air.SulfurDioxide*20).label('SulfurDioxide')).filter(Air.Id==station, Air.Time/1000000-year>=0, Air.Time/1000000-year<1).all()], 'SulfurDioxide'))
    res.append(getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, Air.PM10).filter(Air.Id==station, Air.Time/1000000-year>=0, Air.Time/1000000-year<1).all()], 'PM10'))
    res.append(getaqi([dict(zip(result.keys(), result)) for result in db.session.query(Air.Time, (Air.VisibilityReduction*20).label('VisibilityReduction')).filter(Air.Id==station, Air.Time/1000000-year>=0, Air.Time/1000000-year<1).all()], 'VisibilityReduction'))
    return jsonify(res)

@app.route('/chart5', methods=['POST'])
def chart5():
    year = int(request.form['year'])
    polution = request.form['polution']
    res = [dict(zip(result.keys(), result)) for result in db.session.query(Air.Station, func.sum(getattr(Air, polution)).label(polution)).filter(Air.Time / 1000000 - year >= 0, Air.Time / 1000000 - year < 1).group_by(Air.Station).all()]
    for val in res:
        if val[polution] == None:
            val[polution] = 0
    res.sort(key=lambda d:d[polution], reverse=True)
    res = res[:3]
    summ = res[0][polution]+res[1][polution]+res[2][polution]
    for val in res:
        val[polution] = val[polution]/summ
    return jsonify(res)
if __name__ == 'app':
    db.init_app(app)
    app.run()
