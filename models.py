from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import dateutil.parser

db = SQLAlchemy()

def setup_db(app):
    app.config.from_object('config')
    db.app = app
    migrate = Migrate(app, db)
    db.init_app(app)
    return db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))    
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, default='')
    genres = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def get_shows(self):
       upcoming_shows = [] 
       past_shows = []    
       shows = Show.query.filter_by(venue_id=self.id).all()
       for show in shows:   
          current_time = dateutil.parser.parse(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))     
          show_start_time = dateutil.parser.parse(dateutil.parser.parse(show.start_time).strftime("%d/%m/%Y %H:%M:%S"))    
          if show_start_time > current_time:
            upcoming_shows.append(show)
          else:
            past_shows.append(show) 
       return { 'upcoming_shows' : upcoming_shows, 'past_shows' : past_shows }

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))   
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, default='')
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def get_shows(self):
       upcoming_shows = [] 
       past_shows = []    
       shows = Show.query.filter_by(artist_id=self.id).all()
       for show in shows:   
          current_time = dateutil.parser.parse(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))     
          show_start_time = dateutil.parser.parse(dateutil.parser.parse(show.start_time).strftime("%d/%m/%Y %H:%M:%S"))    
          if show_start_time > current_time:
            upcoming_shows.append(show)
          else:
            past_shows.append(show) 
       return { 'upcoming_shows' : upcoming_shows, 'past_shows' : past_shows }

    def __repr__(self):
      return f'<Artist {self.id} name: {self.name}>'

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.String(120), nullable=False, default=f"{datetime.utcnow().isoformat()[:-3]}Z")

  def __repr__(self):
    return f'<Show {self.id} artist_id: {self.artist_id} venue_id: {self.venue_id}>'
