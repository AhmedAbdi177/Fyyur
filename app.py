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
from sqlalchemy.ext.hybrid import hybrid_property
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime
from sys import exc_info

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.JSON)
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String)
    website = db.Column(db.String)

    @hybrid_property
    def upcoming_shows(self):
        return list(filter(lambda x: x.start_time > datetime.now(),
                                                  self.shows))

    @hybrid_property
    def past_shows(self):
        return list(filter(lambda x: x.start_time <
                             datetime.now(), self.shows))


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.JSON)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String)

    @hybrid_property
    def upcoming_shows(self):
        return list(filter(lambda x: x.start_time > datetime.now(),
                                                  self.shows))

    @hybrid_property
    def past_shows(self):
        return list(filter(lambda x: x.start_time <
                             datetime.now(), self.shows))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer,db.ForeignKey('venue.id',onupdate='CASCADE', ondelete='CASCADE'))
    artist_id = db.Column(db.Integer,db.ForeignKey('artist.id',onupdate='CASCADE', ondelete='CASCADE'))
    start_time = db.Column(db.DateTime())

    artist = db.relationship("Artist", backref=db.backref("shows", lazy=True))
    venue = db.relationship("Venue", backref=db.backref("shows", lazy=True))
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
    # DONE: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venue_areas = db.session.query(db.distinct(Venue.city), Venue.state).all()
    data = []
    for area in venue_areas:
        area_data = {'city': area[0], 'state': area[1], 'venues': []}
        venues = Venue.query.filter_by(city=area[0], state=area[1]).all()
        for venue in venues:
            venue_data = {
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(venue.upcoming_shows)
            }
            area_data['venues'].append(venue_data)
        data.append(area_data)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    query = request.form.get("search_term", "")
    like_query = '%{}%'.format(query)
    results = db.session.query(Venue).filter(
        Venue.name.ilike(like_query)).options(
            db.load_only(Venue.id, Venue.name)).all()
    response = {
        'count': len(results),
        'data': [{
            'id': result.id,
            'name': result.name
        } for result in results]
    }
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    venue = db.session.query(Venue).get(venue_id)
    data = {
        'id':
        venue.id,
        'name':
        venue.name,
        'genres':
        venue.genres,
        'address':
        venue.address,
        'city':
        venue.city,
        'state':
        venue.state,
        'phone':
        venue.phone,
        'website':
        venue.website,
        'facebook_link':
        venue.facebook_link,
        'seeking_talent':
        venue.seeking_talent,
        'seeking_description':
        venue.seeking_description,
        'image_link':
        venue.image_link,
        'past_shows': [{
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
        } for show in venue.past_shows],
        'upcoming_shows': [{
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
        } for show in venue.upcoming_shows],
        'past_shows_count':
        len(venue.past_shows),
        'upcoming_shows_count':
        len(venue.upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    # DONE: insert form data as a new Venue record in the db, instead
    data = Venue(name=form.name.data,
                 city=form.city.data,
                 state=form.state.data,
                 address=form.address.data,
                 phone=form.phone.data,
                 image_link=form.image_link.data,
                 facebook_link=form.facebook_link.data,
                 genres=form.genres.data,
                 seeking_talent=form.seeking_talent.data,
                 seeking_description=form.seeking_description.data,
                 website=form.website_link.data)
    # DONE: modify data to be the data object returned from db insertion
    try:
        db.session.add(data)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + data.name + '  was successfully listed!')
    except Exception as e:
        print(e)
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        flash('An error occurred. Venue ' + data.name +
              ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("venues"))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = db.session.query(Venue).get(venue_id)
    if (venue is None):
        return not_found_error(404)
    try:
        venue_del = db.session.query(Venue).filter(Venue.id == venue_id)
        venue_del.delete()
        db.session.commit()
        flash("Venue: " + venue.name + " was successfully deleted.")
    except:
        db.session.rollback()
        print(exc_info())
        flash("Venue: " + venue.name +
              " could not be deleted successfully.Try again later")
    finally:
        db.session.close()
    return redirect(url_for('venues'))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = db.session.query(Artist).order_by(db.asc(Artist.name)).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    query = request.form.get("search_term", "")
    like_query = '%{}%'.format(query)
    results = db.session.query(Artist).filter(
        Artist.name.ilike(like_query)).all()
    response = {
        "count":
        len(results),
        "data": [{
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(result.upcoming_shows),
        } for result in results]
    }
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id
    artist = db.session.query(Artist).get(artist_id)
    data = {
        'id':
        artist.id,
        'name':
        artist.name,
        'genres':
        artist.genres,
        'city':
        artist.city,
        'state':
        artist.state,
        'phone':
        artist.phone,
        'website':
        artist.website,
        'facebook_link':
        artist.facebook_link,
        'seeking_venue':
        artist.seeking_venue,
        'seeking_description':
        artist.seeking_description,
        'image_link':
        artist.image_link,
        'past_shows': [{
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': str(show.start_time)
        } for show in artist.past_shows],
        'upcoming_shows': [{
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': str(show.start_time)
        } for show in artist.upcoming_shows],
        'past_shows_count':
        len(artist.past_shows),
        'upcoming_shows_count':
        len(artist.upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    if (artist is None):
        return not_found_error(404)
    artist_data = artist.__dict__
    form.name.data = artist_data['name']
    form.city.data = artist_data['city']
    form.state.data = artist_data['state']
    form.phone.data = artist_data['phone']
    form.genres.data = artist_data['genres']
    form.facebook_link.data = artist_data['facebook_link']
    form.image_link.data = artist_data['image_link']
    form.website_link.data = artist_data['website']
    form.seeking_venue.data = artist_data['seeking_venue']
    form.seeking_description.data = artist_data['seeking_description']

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    try:
        db.session.query(Artist).filter_by(id=artist_id).update(
            dict(name=form.name.data,
                 city=form.city.data,
                 state=form.state.data,
                 phone=form.phone.data,
                 image_link=form.image_link.data,
                 facebook_link=form.facebook_link.data,
                 genres=form.genres.data,
                 seeking_venue=form.seeking_venue.data,
                 seeking_description=form.seeking_description.data,
                 website=form.website_link.data))

        db.session.commit()
        flash('Artist edited successfully')
    except:
        print(exc_info())
        flash('An error occurred. Artist could not be edited')
        db.session.rollback()
    finally:
        db.session.close()
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if (venue is None):
        return not_found_error(404)
    venue_data = venue.__dict__
    form.name.data = venue_data['name']
    form.city.data = venue_data['city']
    form.state.data = venue_data['state']
    form.phone.data = venue_data['phone']
    form.address.data = venue_data['address']
    form.genres.data = venue_data['genres']
    form.facebook_link.data = venue_data['facebook_link']
    form.image_link.data = venue_data['image_link']
    form.website_link.data = venue_data['website']
    form.seeking_talent.data = venue_data['seeking_talent']
    form.seeking_description.data = venue_data['seeking_description']
    # DONE: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    try:
        db.session.query(Venue).filter_by(id=venue_id).update(
            dict(name=form.name.data,
                 city=form.city.data,
                 state=form.state.data,
                 phone=form.phone.data,
                 address=form.address.data,
                 image_link=form.image_link.data,
                 facebook_link=form.facebook_link.data,
                 genres=form.genres.data,
                 seeking_talent=form.seeking_talent.data,
                 seeking_description=form.seeking_description.data,
                 website=form.website_link.data))

        db.session.commit()
        flash('Venue edited successfully')
    except:
        print(exc_info())
        flash('An error occurred. Venue could not be edited')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    # DONE: insert form data as a new Venue record in the db, instead
    data = Artist(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  image_link=form.image_link.data,
                  facebook_link=form.facebook_link.data,
                  genres=form.genres.data,
                  seeking_venue=form.seeking_venue.data,
                  seeking_description=form.seeking_description.data,
                  website=form.website_link.data)
    # DONE: modify data to be the data object returned from db insertion
    try:
        db.session.add(data)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + data.name + '  was successfully listed!')
    except Exception as e:
        print(e)
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' + data.name +
              ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("artists"))


#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.

    shows = db.session.query(Show).order_by().all()

    data = [{
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': str(show.start_time)
    } for show in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead
    form = ShowForm()

    data = Show(artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data)
    try:
        db.session.add(data)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        print(e)
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("shows"))

    # on successful db insert, flash success
    #flash('Show was successfully listed!')
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    #return render_template('pages/home.html')

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
