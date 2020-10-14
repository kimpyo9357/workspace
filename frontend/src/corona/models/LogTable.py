from corona.models import db

class LobTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(70), nullable=False)

    def __repr__(self):
        return '<%s : %d>' % (self.date, self.count)