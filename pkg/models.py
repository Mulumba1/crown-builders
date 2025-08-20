from datetime import datetime
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()


class ContactUs(db.Model):
    __tablename__ = 'contact_us'  
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.String(10), default="unread")


class Admin(db.Model):
    admin_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    admin_email = db.Column(db.String(120), unique=True, nullable=False)  
    admin_password = db.Column(db.String(255), nullable=False)  
    admin_profile_pic = db.Column(db.String(255), default="default.jpg")  
    admin_lastlogin = db.Column(db.DateTime(), default=datetime.utcnow)


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(225), nullable=False)
    description = db.Column(db.Text)  
    position = db.Column(db.String(225), nullable=False)
    image = db.Column(db.String(255), default="default.jpg")  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Team {self.name} ({self.position})>"
    



class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    full_description = db.Column(db.Text)
    client = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    category = db.Column(db.Enum('Residential', 'Hotel', 'Commercial', 'Factory', 'Hostel', name='category_enum'), nullable=False)
    year_completed = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ProjectImage', backref='project', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.title} ({self.category})>"


class ProjectImage(db.Model):
    __tablename__ = 'project_image'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    def __repr__(self):
        return f"<ProjectImage {self.filename}>"




class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50))
    type = db.Column(db.String(50))
    size = db.Column(db.Float)
    rooms = db.Column(db.Integer)
    location = db.Column(db.String(100))
    short_description = db.Column(db.Text)
    full_description = db.Column(db.Text)
    main_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-many relationship with images
    gallery = db.relationship('DesignImage', backref='design', lazy=True, cascade="all, delete-orphan")


class DesignImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    design_id = db.Column(db.Integer, db.ForeignKey('design.id'), nullable=False)





class FloorStamp(db.Model):
    __tablename__ = 'floor_stamps'  
    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(120), nullable=False)
    short_description = db.Column(db.Text)
    full_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('FloorImage', backref='floor_stamp', lazy=True)


class FloorImage(db.Model):
    __tablename__ = 'floor_images'  
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor_stamps.id'), nullable=False)



class LandScape(db.Model):
    __tablename__ = 'landscape'

    id = db.Column(db.Integer, primary_key=True)
    design = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    full_description = db.Column(db.Text)
    client = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    year_completed = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('LandImage', backref='landscape', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LandScape {self.design}>"



class LandImage(db.Model):
    __tablename__ = 'land_image'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    landscape_id = db.Column(db.Integer, db.ForeignKey('landscape.id'), nullable=False)

    def __repr__(self):
        return f"<LandImage {self.filename}>"
