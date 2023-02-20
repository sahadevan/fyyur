#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

    def num_upcoming_shows(self):
       num_upcoming_shows = 0
       current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
       shows = Show.query.filter_by(artist_id=self.id).all()
       for show in shows:
          print(f'Upcoming Shows: {num_upcoming_shows}, Show Start Time: {show.start_time}')
          if show.start_time > current_time:
            num_upcoming_shows += 1          
       
       return { 'num_upcoming_shows' : num_upcoming_shows }

    def __repr__(self):
      return f'<Artist {self.id} name: {self.name}>'

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.String(120), nullable=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

  def __repr__(self):
    return f'<Show {self.id} artist_id: {self.artist_id} venue_id: {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  error = False
  try:
    venues = Venue.query.all()
    for venue in venues:
      data.append({
              'city' : venue.id,
              'name' : venue.name
          })
  except:
    error = True
  if error:
    flash('An error occurred. Venues cannot be listed.')

  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False  
  try: 
   name = request.form['name']
   city = request.form['city']
   state = request.form['state']
   address = request.form['address']
   phone = request.form['phone']
   image_link = request.form['image_link']
   facebook_link = request.form['facebook_link']
   website = request.form['website_link']
   seeking_talent = True if request.form['seeking_talent'] == 'y' else False
   seeking_description = request.form['seeking_description']
   genres = ','.join(request.form.getlist('genres'))
   venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = image_link, facebook_link = facebook_link, website = website, seeking_talent = seeking_talent, seeking_description= seeking_description, genres = genres)  
  
   db.session.add(venue)
   db.session.commit()
  except:   
    db.session.rollback() 
    error = True 
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  error = False
  try:
    artists = Artist.query.all()
    for artist in artists:
      data.append({
              'id' : artist.id,
              'name' : artist.name
          })
  except:
    error = True
  if error:
    flash('An error occurred. Artists cannot be listed.')

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists(): 
  error = False  
  data = []
  response = {}
  try:  
    artistsResult = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term') + '%'))    
    count = artistsResult.count() 
    if count > 0:
      for artist in artistsResult:             
        #num_upcoming_shows = artist.num_upcoming_shows()
        data.append({
          'id': artist.id,
          'name': artist.name,
          'num_upcoming_shows': 0
        })

      response = {
        'count': count,
        'data': data
      }
      print(response)
    else:
      flash('Please refrain your search...')
  except: 
    error = True 

  if error:
    flash('Error while filtering Artists with the search term -' + request.form['search_term'])

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows' : [],
    'upcoming_shows': [],
    'past_shows_count' : 0,
    'upcoming_shows_count' : 0
  }

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    artist_details = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    
    if artist_details:
     form.name.data = artist_details['name']
     form.genres.data = artist_details['genres']
     form.city.data = artist_details['city']
     form.state.data = artist_details['state']
     form.phone.data = artist_details['phone']
     form.website_link.data = artist_details['website']
     form.facebook_link.data = artist_details['facebook_link']
     form.seeking_venue.data = artist_details['seeking_venue']
     form.seeking_description.data = artist_details['seeking_description']
     form.image_link.data = artist_details['image_link']
  except:
    flash('Unable to edit Artist')
    artist_details = {
        "id": -1,
        "name": '',
        "genres": '',
        "city": '',
        "state": '',
        "phone": '',
        "website": '',
        "facebook_link": '',
        "seeking_venue": '',
        "seeking_description": '',
        "image_link": ''
    }

  return render_template('forms/edit_artist.html', form=form, artist=artist_details)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False  
  try:  
   name = request.form['name']
   city = request.form['city']
   state = request.form['state']
   phone = request.form['phone']
   image_link = request.form['image_link']
   facebook_link = request.form['facebook_link']
   website = request.form['website_link']
   seeking_venue = True if request.form['seeking_venue'] == 'y' else False
   seeking_description = request.form['seeking_description']
   genres = ','.join(request.form.getlist('genres'))
   artist = Artist.query.get(artist_id) 
   artist.name = name
   artist.city = city
   artist.state = state
   artist.phone = phone
   artist.image_link = image_link
   artist.facebook_link = facebook_link
   artist.website = website
   artist.seeking_venue = seeking_venue
   artist.seeking_description = seeking_description
   artist.genres = genres

   db.session.commit()
  except:   
    db.session.rollback() 
    error = True 
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist could not be updated.')
  else:
    flash('Artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    venue_details = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    
    if venue_details:
     form.name.data = venue_details['name']
     form.genres.data = venue_details['genres']
     form.city.data = venue_details['city']
     form.state.data = venue_details['state']
     form.address.data = venue_details['address']
     form.phone.data = venue_details['phone']
     form.website_link.data = venue_details['website']
     form.facebook_link.data = venue_details['facebook_link']
     form.seeking_talent.data = venue_details['seeking_talent']
     form.seeking_description.data = venue_details['seeking_description']
     form.image_link.data = venue_details['image_link']
  except:
    flash('Unable to edit Venue')
    venue_details = {
        "id": -1,
        "name": '',
        "genres": '',
        "city": '',
        "state": '',
        "phone": '',
        "address": '',
        "website": '',
        "facebook_link": '',
        "seeking_venue": '',
        "seeking_description": '',
        "image_link": ''
    }
  return render_template('forms/edit_venue.html', form=form, venue=venue_details)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False  
  try:  
   name = request.form['name']
   city = request.form['city']
   state = request.form['state']
   phone = request.form['phone']
   address = request.form['address']
   image_link = request.form['image_link']
   facebook_link = request.form['facebook_link']
   website = request.form['website_link']
   seeking_venue = True if request.form['seeking_venue'] == 'y' else False
   seeking_description = request.form['seeking_description']
   genres = ','.join(request.form.getlist('genres'))
   venue = Venue.query.get(venue_id) 
   venue.name = name
   venue.city = city
   venue.state = state
   venue.phone = phone
   venue.image_link = image_link
   venue.facebook_link = facebook_link
   venue.website = website
   venue.seeking_venue = seeking_venue
   venue.seeking_description = seeking_description
   venue.genres = genres
   venue.address = address

   db.session.commit()
  except:   
    db.session.rollback() 
    error = True 
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue could not be updated.')
  else:
    flash('Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False  
  try:  
   name = request.form['name']
   city = request.form['city']
   state = request.form['state']
   phone = request.form['phone']
   image_link = request.form['image_link']
   facebook_link = request.form['facebook_link']
   website = request.form['website_link']
   seeking_venue = True if request.form['seeking_venue'] == 'y' else False
   seeking_description = request.form['seeking_description']
   genres = ','.join(request.form.getlist('genres'))
   artist = Artist(name = name, city = city, state = state, phone = phone, image_link = image_link, facebook_link = facebook_link, website = website, seeking_venue = seeking_venue, seeking_description= seeking_description, genres = genres)  
 
   db.session.add(artist)
   db.session.commit()
  except:   
    db.session.rollback() 
    error = True 
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  error = False
  try:
    shows = Show.query.all()
    for show in shows:
      data.append({
              'venue_id' :show.venue_id,
              'venue_name' :show.Venue.name,
              'artist_id' :show.artist_id,
              'artist_name' :show.Artist.name,
              'artist_image_link' :show.Artist.image_link,
              'start_time' :show.start_time
          })
  except:
    error = True
  if error:
    flash('An error occurred. Shows cannot be listed.')
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False  
  try:  
   artist_id = request.form['artist_id']
   venue_id = request.form['venue_id']
   start_time = request.form['start_time']
   show = Show(artist_id = artist_id, venue_id=venue_id, start_time=start_time)  
   db.session.add(show)
   db.session.commit()
  except:   
    db.session.rollback() 
    error = True 
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
