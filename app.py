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

from models import setup_db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = setup_db(app)

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
    state_and_city = {}    
    for venue in venues:  
      if venue.state in state_and_city.keys():
        if venue.city not in state_and_city[venue.state]:
          state_and_city[venue.state].append(venue.city)
      else:    
        state_and_city[venue.state] = [venue.city]
    
    for state in state_and_city:
       for city in state_and_city[state]:
         for venue in venues:
           venue_details = []
           if venue.state == state and venue.city == city:
             venue_details.append({ 
              'id' : venue.id,
              'name': venue.name,
              'num_upcoming_shows': len(venue.get_shows()['upcoming_shows'])
             })
         data.append({
            'city': city,
            'state': state,
            'venues': venue_details
          })
  except:
    error = True
  if error:
    flash('An error occurred. Venues cannot be listed.')

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  error = False  
  data = []
  response = {}
  try:  
    venuesResult = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term') + '%'))    
    count = venuesResult.count() 
    if count > 0:
      for venue in venuesResult:             
        num_upcoming_shows = len(venue.get_shows()['upcoming_shows'])
        data.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_upcoming_shows
        })

      response = {
        'count': count,
        'data': data
      }
    else:
      flash('Please refine your search...')
  except: 
    error = True 

  if error:
    flash('Error while filtering Venues with the search term -' + request.form['search_term'])

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  venue_upcoming_shows = venue.get_shows()['upcoming_shows']
  upcoming_shows = []
  
  for upcoming_show in venue_upcoming_shows:
    artist = Artist.query.get(upcoming_show.artist_id)
    upcoming_shows.append({ 'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': upcoming_show.start_time  })

  venue_past_shows = venue.get_shows()['past_shows']
  past_shows = []

  for past_show in venue_past_shows:
    artist = Artist.query.get(past_show.artist_id)
    past_shows.append({ 'artist_id': artist.id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': past_show.start_time  })

  num_upcoming_shows = len(venue_upcoming_shows)
  num_past_shows = len(venue_past_shows)
  data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'address': venue.address,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'genres' : venue.genres.split(','),
    'past_shows' : past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count' : num_past_shows,
    'upcoming_shows_count' : num_upcoming_shows
  }

  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
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
        num_upcoming_shows = len(artist.get_shows()['upcoming_shows'])
        data.append({
          'id': artist.id,
          'name': artist.name,
          'num_upcoming_shows': num_upcoming_shows
        })

      response = {
        'count': count,
        'data': data
      }
    else:
      flash('Please refine your search...')
  except: 
    error = True 

  if error:
    flash('Error while filtering Artists with the search term -' + request.form['search_term'])

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist_upcoming_shows = artist.get_shows()['upcoming_shows']
  upcoming_shows = []
  
  for upcoming_show in artist_upcoming_shows:
    venue = Venue.query.get(upcoming_show.venue_id)
    upcoming_shows.append({ 'venue_id': venue.id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': upcoming_show.start_time  })

  artist_past_shows = artist.get_shows()['past_shows']
  past_shows = []

  for past_show in artist_past_shows:
    venue = Venue.query.get(past_show.venue_id)
    past_shows.append({ 'venue_id': venue.id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': past_show.start_time  })

  num_upcoming_shows = len(artist_upcoming_shows)
  num_past_shows = len(artist_past_shows)
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
    'genres' : artist.genres.split(','),
    'past_shows' : past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count' : num_past_shows,
    'upcoming_shows_count' : num_upcoming_shows
  }

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
        "seeking_talent": '',
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
   seeking_talent = True if request.form['seeking_talent'] == 'y' else False
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
   venue.seeking_talent = seeking_talent
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
   start_time = f"{dateutil.parser.parse(request.form['start_time']).isoformat()}Z"
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
