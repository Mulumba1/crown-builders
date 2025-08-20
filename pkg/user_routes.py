import os, random, string, uuid
from uuid import uuid4
from datetime import datetime,date
from flask import render_template
from flask import render_template,request,redirect,flash,url_for,session,g,flash,jsonify
from pkg import app
from pkg.models import db,ContactUs,Admin,Project,ProjectImage, Design, FloorStamp,LandScape, Team
from pkg.models import db



@app.route('/')
def home():   
    return render_template("user/index.html")


@app.route('/about')
def about():  
    teams = Team.query.all()  
    return render_template("user/about.html", teams=teams)


@app.route('/services')
def services():    
    return render_template("user/services.html")

@app.route('/team')
def team_members():    
    teams = Team.query.all()
    return render_template("user/team.html", teams=teams)




@app.route('/team-details/<int:id>')
def team_details(id):
    team = Team.query.get_or_404(id)
    return render_template('user/team_details.html', team=team)

@app.route('/designs')
def designs(): 
    designs = Design.query.all()    
    return render_template("user/design.html", designs=designs)


@app.route('/floor-stamping')
def floor_stamping(): 
    floors = FloorStamp.query.all()    
    return render_template("user/floor-stamping.html", floors=floors)


@app.route('/land-scape')
def landscape(): 
    designs = LandScape.query.all()    
    return render_template("user/landscape.html", designs=designs)



@app.route('/projects')
def projects():    
    projects = Project.query.all()  
    return render_template("user/projects.html", projects=projects)





@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Basic validation
        if not name or not email or not subject or not message:
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'})

        # Process and save the form data
        new_contact = ContactUs(
            name=name,
            email=email,
            subject=subject,
            phone=phone,
            message=message
        )
        try:
            db.session.add(new_contact)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Thank you for contacting Crown Builders, One of our Representative will reach out to you within 2 working Days'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})
        
    return render_template("user/contact.html")



