from database import db
import math

class Air(db.Model):
    __tablename__ = 'air'

    Time = db.Column(db.Integer, primary_key=True)
    Id = db.Column(db.Integer, primary_key=True)
    Station = db.Column(db.String(50))
    Longitude = db.Column(db.Float)
    Latitude = db.Column(db.Float)
    CarbonMonoxide = db.Column(db.Float)
    Ozone = db.Column(db.Float)
    NitrogenDioxide = db.Column(db.Float)
    SulfurDioxide = db.Column(db.Float)
    PM25 = db.Column(db.Float)
    PM10 = db.Column(db.Float)
    VisibilityReduction = db.Column(db.Float)
    AQI = db.Column(db.Float)
    Summary = db.Column(db.Float)


    def __init__(self, Time, Id, Station, Longitude, Latitude, CarbonMonoxide, Ozone, NitrogenDioxide, SulfurDioxide, PM25, PM10, VisibilityReduction, AQI, Summary):
        self.Time = Time
        self.Id = Id
        self.Station = Station
        self.Longitude = Longitude
        self.Latitude = Latitude
        self.CarbonMonoxide = CarbonMonoxide
        self.Ozone = Ozone
        self.NitrogenDioxide = NitrogenDioxide
        self.SulfurDioxide = SulfurDioxide
        self.PM25 = PM25
        self.PM10 = PM10
        self.VisibilityReduction = VisibilityReduction
        self.AQI = AQI
        if Summary == 'VERY GOOD':
            self.Summary = 5
        elif Summary == 'GOOD':
            self.Summary = 4
        elif Summary == 'FAIR':
            self.Summary = 3
        elif Summary == 'POOR':
            self.Summary = 2
        elif Summary == 'VERY POOR':
            self.Summary = 1
        else:
            self.Summary = float('nan')