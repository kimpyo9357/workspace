from corona.models import db

class DailyConfirmed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    ''''code = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Char, nullable = False)'''
    
    def __repr__(self):
        return '<%s : %d>' % (self.smalldatetime, self.code)
