# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass


class Users(db.Model, UserMixin):

    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.LargeBinary)

    oauth_github  = db.Column(db.String(100), nullable=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

    @classmethod
    def find_by_email(cls, email: str) -> "Users":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username: str) -> "Users":
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, _id: int) -> "Users":
        return cls.query.filter_by(id=_id).first()
   
    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
          
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
    
    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)


# Definisikan model untuk tabel tabel_kriteria
class tabelKriteria(db.Model):
    __tablename__ = 'tabel_kriteria'

    id = db.Column(db.Integer, primary_key=True)
    nama_kriteria = db.Column(db.String(255))
    penjelasan_kriteria = db.Column(db.Text)

    def __init__(self, nama_kriteria, penjelasan_kriteria):
        self.nama_kriteria = nama_kriteria
        self.penjelasan_kriteria = penjelasan_kriteria
        
# Definisikan model untuk tabel tabel_peringkat
class tabelRanking(db.Model):
    __tablename__ = 'tabel_peringkat'

    id = db.Column(db.Integer, primary_key=True)
    peringkat = db.Column(db.Integer)
    alternatif_akun = db.Column(db.String(100))
    alternatif_id = db.Column(db.Integer, db.ForeignKey('tabel_alternatif.id'))
    leaving_flow = db.Column(db.Float)
    entering_flow = db.Column(db.Float)
    net_flow = db.Column(db.Float)

    # Definisikan relasi dengan tabel_alternatif
    alternatif = db.relationship('tabelAlternative', back_populates='rankings')

    def __init__(self, peringkat, alternatif_akun, alternatif_id, leaving_flow, entering_flow, net_flow):
        self.peringkat = peringkat
        self.alternatif_akun = alternatif_akun
        self.alternatif_id = alternatif_id
        self.leaving_flow = leaving_flow
        self.entering_flow = entering_flow
        self.net_flow = net_flow

# Definisikan model untuk tabel tabel_alternatif
class tabelAlternative(db.Model):
    __tablename__ = 'tabel_alternatif'

    id = db.Column(db.Integer, primary_key=True)
    alternatif_akun = db.Column(db.String(100))
    total_follower = db.Column(db.Integer) # Benefit
    total_likes = db.Column(db.Integer) # Benefit
    overall_engagement = db.Column(db.Float) # Benefit
    likes_rate = db.Column(db.Float) # Benefit
    shares_rate = db.Column(db.Float) # Benefit
    average_view = db.Column(db.Integer) # Benefit
    average_likes = db.Column(db.Integer) # Benefit
    average_share = db.Column(db.Integer) # Benefit
    harga = db.Column(db.Integer) # Cost
    kategori = db.Column(db.Text)

    # Definisikan relasi dengan tabel_peringkat
    rankings = db.relationship('tabelRanking', back_populates='alternatif')

    def __init__(self, alternatif_akun, total_follower, total_likes, overall_engagement, 
                 likes_rate, shares_rate, average_view, average_likes, average_share, harga, kategori):
        self.alternatif_akun = alternatif_akun
        self.total_follower = total_follower
        self.total_likes = total_likes
        self.overall_engagement = overall_engagement
        self.likes_rate = likes_rate
        self.shares_rate = shares_rate
        self.average_view = average_view
        self.average_likes = average_likes
        self.average_share = average_share
        self.harga = harga
        self.kategori = kategori
