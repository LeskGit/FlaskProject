asso = db.Table('asso',
                db.Column('music_id', db.Integer,
                          db.ForeignKey('music.id')),
                db.Column('genre_id', db.Integer,
                          db.ForeignKey('genre.id'))
                )


class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))

    artist_id = db.Column(db.Integer,
                          db.ForeignKey("artist.id"))
    artiste = db.relationship("Artist",
                              backref=db.backref("musics", lazy="dynamic"))
    genres = db.relationship(  
                             lazy='subquery',
                             backref=db.backref('musics', lazy=True))
