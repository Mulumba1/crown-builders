import os, random, uuid, string
from uuid import uuid4
from flask import render_template,request,redirect,flash,url_for,session,g,flash,jsonify,send_file,current_app
from flask_mail import Message
from functools import wraps
from sqlalchemy import or_
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from pkg import app, mail
from pkg.models import db,ProjectImage, Project, Admin, ContactUs, Design, DesignImage, FloorStamp, FloorImage, LandScape, LandImage, Team
from pkg.register_forms import RegisterForm

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash("Please log in first!", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function



ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS




@app.route('/admin/add-project', methods=['GET', 'POST'])
@admin_required
def add_project():
    current_year = datetime.now().year
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    if request.method == 'POST':
        title = request.form['title']
        short_desc = request.form['short_description']
        full_desc = request.form.get('full_description', '')
        client = request.form['client']
        location = request.form['location']
        category = request.form['category']
        year_completed = request.form.get('year_completed', None)
        files = request.files.getlist('images')

        if not files or len(files) > 30:
            flash("Please upload up to 30 images.", "danger")
            return redirect(request.url)

        try:
            new_project = Project(
                title=title,
                short_description=short_desc,
                full_description=full_desc,
                client=client,
                location=location,
                category=category,
                year_completed=int(year_completed) if year_completed else None
            )
            db.session.add(new_project)
            db.session.commit()

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image = ProjectImage(filename=filename, project_id=new_project.id)
                    db.session.add(image)

            db.session.commit()
            flash("Project with images uploaded!", "success")
            return redirect(url_for('project_list'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error uploading project: {e}", "danger")

    return render_template('admin/add_project.html',
    unread_messages=unread_messages, current_admin=g.admin, current_year=current_year)




@app.route('/manage/project/')
@admin_required
def manage_projects():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()

    query = Project.query
    if search_query:
        query = query.filter(
            or_(
                Project.title.ilike(f"%{search_query}%"),
                Project.location.ilike(f"%{search_query}%"),
                Project.category.ilike(f"%{search_query}%")
            )
        )

    projects = query.paginate(page=page, per_page=10)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'html': render_template('admin/projects_table.html', projects=projects)})

    return render_template(
        'admin/manage_projects.html',
        projects=projects,
        unread_messages=unread_messages,
        search_query=search_query,
        current_admin=g.admin
    )




@app.route('/admin/project/edit/<int:id>/', methods=['GET', 'POST'])
@admin_required
def edit_project(id):
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        project.title = request.form['name']
        project.short_description = request.form['short_description']
        project.full_description = request.form['full_description']

        images_to_delete = request.form.getlist('delete_images')
        for img_id in images_to_delete:
            img = ProjectImage.query.get(int(img_id))
            if img and img.project_id == project.id:
                db.session.delete(img)

        existing_images_count = ProjectImage.query.filter_by(project_id=project.id).count()
        uploaded_files = request.files.getlist('images')

        for file in uploaded_files:
            if file.filename and existing_images_count < 30:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_img = DesignImage(project_id=project.id, filename=filename)
                db.session.add(new_img)
                existing_images_count += 1

        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('manage_projects'))

    images = ProjectImage.query.filter_by(project_id=project.id).all()
    return render_template(
        'admin/edit_project.html',
        project=project,
        images=images,
        unread_messages=unread_messages,
        current_admin=g.admin
    )




@app.route('/project-details/<int:id>')
def project_details(id):
    project = Project.query.get_or_404(id)
    return render_template('user/project_details.html', project=project)



@app.route('/admin/projects/delete/<int:id>/', methods=['DELETE'])
@admin_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Project deleted successfully!'})


# Architectural Designs starts here

@app.route('/admin/add-design', methods=['GET', 'POST'])
@admin_required
def add_design():
    current_year = datetime.now().year
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    if request.method == 'POST':
        title = request.form['title']
        short_desc = request.form['short_description']
        full_desc = request.form.get('full_description', '')
        location = request.form['location']
        category = request.form['category']
        files = request.files.getlist('images')

        if not files or len(files) > 30:
            flash("Please upload up to 30 images.", "danger")
            return redirect(request.url)

        try:
            new_design = Design(
                title=title,
                short_description=short_desc,
                full_description=full_desc,
                location=location,
                category=category,
                
            )
            db.session.add(new_design)
            db.session.commit()

            for file in files:
                print("Processing file:", file.filename)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image = DesignImage(filename=filename, design_id=new_design.id)
                    db.session.add(image)
           
            db.session.commit()
            flash("Design images uploaded!", "success")
            return redirect(url_for('design_list'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error uploading image: {e}", "danger")

    return render_template('admin/add_design.html',
    unread_messages=unread_messages, current_admin=g.admin, current_year=current_year)



@app.route('/admin/design/edit/<int:id>/', methods=['GET', 'POST'])
@admin_required
def edit_design(id):
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    design = Design.query.get_or_404(id)

    if request.method == 'POST':
        design.title = request.form['title']
        design.short_description = request.form['short_description']
        design.full_description = request.form['full_description']

        images_to_delete = request.form.getlist('delete_images')
        for img_id in images_to_delete:
            img = DesignImage.query.get(int(img_id))
            if img and img.design_id == design.id:
                db.session.delete(img)

        existing_images_count = DesignImage.query.filter_by(design_id=design.id).count()
        uploaded_files = request.files.getlist('images')

        for file in uploaded_files:
            if file.filename and existing_images_count < 30:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                new_img = DesignImage(design_id=design.id, filename=filename)
                db.session.add(new_img)
                existing_images_count += 1

        db.session.commit()
        flash('Design updated successfully!', 'success')
        return redirect(url_for('manage_designs'))

    images = DesignImage.query.filter_by(design_id=design.id).all()
    return render_template(
        'admin/edit_design.html',
        design=design,
        images=images,
        unread_messages=unread_messages,
        current_admin=g.admin
    )




@app.route('/manage/design/')
@admin_required
def manage_designs():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()

    query = Design.query
    if search_query:
        query = query.filter(
            or_(
                Design.title.ilike(f"%{search_query}%"),      
                Design.location.ilike(f"%{search_query}%"),  
                Design.category.ilike(f"%{search_query}%")    
            )
        )

    designs = query.paginate(page=page, per_page=10)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'html': render_template('admin/designs_table.html', designs=designs)})

    return render_template(
        'admin/manage_designs.html',
        designs=designs,
        unread_messages=unread_messages,
        search_query=search_query,
        current_admin=g.admin
    )



@app.route('/design-details/<int:id>')
def design_details(id):
    design = Design.query.get_or_404(id)
    return render_template('user/design-details.html', design=design)




@app.route('/admin/designs/delete/<int:id>', methods=['DELETE'])
@admin_required
def delete_design(id):
    print("Delete request received for ID:", id)
    design = Design.query.get_or_404(id)
    db.session.delete(design)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Architectural Design deleted successfully!'})

# Increte Floor Stamping starts here

@app.route('/admin/add-floor', methods=['GET', 'POST'])
@admin_required
def add_floor():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    if request.method == 'POST':
        pattern = request.form['pattern']
        short_desc = request.form['short_description']
        full_desc = request.form.get('full_description', '')
        files = request.files.getlist('images')

        if not files or len(files) > 30:
            flash("Please upload up to 30 images.", "danger")
            return redirect(request.url)

        try:
            new_floor = FloorStamp(
                pattern=pattern,
                short_description=short_desc,
                full_description=full_desc,
                
            )
            db.session.add(new_floor)
            db.session.commit()

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image = FloorImage(filename=filename, floor_id=new_floor.id)
                    db.session.add(image)
           
            db.session.commit()
            flash("Floor Stamping images uploaded!", "success")
            return redirect(url_for('floor_list'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error uploading image: {e}", "danger")

    return render_template('admin/add_floor.html',
    unread_messages=unread_messages, current_admin=g.admin)




@app.route('/manage/floor/')
@admin_required
def manage_floors():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()

    query = FloorStamp.query
    if search_query:
        query = query.filter(
            or_(
                FloorStamp.pattern.ilike(f"%{search_query}%"),
            )
        )

    floors = query.paginate(page=page, per_page=10)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'html': render_template('admin/floors_table.html', floors=floors)})

    return render_template(
        'admin/manage_floors.html',
        floors=floors,
        unread_messages=unread_messages,
        search_query=search_query,
        current_admin=g.admin
    )



@app.route('/floor-details/<int:id>')
def floor_details(id):
    floors = FloorStamp.query.get_or_404(id)
    return render_template('user/floor-details.html', floors=floors)



@app.route('/admin/floors/delete/<int:id>/', methods=['POST'])
@admin_required
def delete_floor(id):
    floor = FloorStamp.query.get_or_404(id)
    db.session.delete(floor)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Floor Stamping deleted successfully!'})




@app.route('/admin/floor/edit/<int:id>/', methods=['GET', 'POST'])
@admin_required
def edit_floor(id):
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    floor = FloorStamp.get_or_404(id)

    if request.method == 'POST':
        floor.pattern = request.form['pattern']
        floor.short_desc = request.form['short_description']
        floor.full_desc = request.form.get('full_description', '')

        db.session.commit()
        flash('Floor Stamping updated successfully!', 'success')
        return redirect(url_for('manage_floors'))

    return render_template(
        'admin/edit_project.html',
        floor=floor,
        unread_messages=unread_messages,
        current_admin=g.admin
    )





# Land Scapping starts here

@app.route('/admin/add-landscaping', methods=['GET', 'POST'])
@admin_required
def add_landscape():
    current_year = datetime.now().year
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    if request.method == 'POST':
        design = request.form['design']
        client = request.form['client']
        short_desc = request.form['short_description']
        full_desc = request.form.get('full_description', '')
        location = request.form['location']
        year_completed = request.form.get('year_completed', None)
        files = request.files.getlist('images')

        if not files or len(files) > 30:
            flash("Please upload up to 30 images.", "danger")
            return redirect(request.url)

        try:
            new_landscape = LandScape(
                design=design,
                short_description=short_desc,
                full_description=full_desc,
                client=client,
                location=location,
                year_completed=int(year_completed) if year_completed else None
                
            )
            db.session.add(new_landscape)
            db.session.commit()

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image = LandImage(filename=filename, landscape_id=new_landscape.id)
                    db.session.add(image)
           
            db.session.commit()
            flash("Landscape images uploaded!", "success")
            return redirect(url_for('landscape_list'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error uploading image: {e}", "danger")

    return render_template('admin/add_landscape.html',
    unread_messages=unread_messages, current_admin=g.admin, current_year=current_year)




@app.route('/manage/landscape/')
@admin_required
def manage_landscape():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()

    query = LandScape.query
    if search_query:
        query = query.filter(
            or_(
                LandScape.design.ilike(f"%{search_query}%"),
                LandScape.location.ilike(f"%{search_query}%")
            )
        )

    designs = query.paginate(page=page, per_page=10)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'html': render_template('admin/landscape_table.html', designs=designs)})

    return render_template(
        'admin/manage_landscape.html',
        designs=designs,
        unread_messages=unread_messages,
        search_query=search_query,
        current_admin=g.admin
    )



@app.route('/landscape-details/<int:id>')
def landscape_details(id):
    design = LandScape.query.get_or_404(id)
    return render_template('user/landscape-details.html', design=design)



@app.route('/admin/landscape/delete/<int:id>/', methods=['POST'])
@admin_required
def delete_landscape(id):
    design = LandScape.query.get_or_404(id)
    db.session.delete(design)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Floor Stamping deleted successfully!'})




@app.route('/admin/landscape/edit/<int:id>/', methods=['GET', 'POST'])
@admin_required
def edit_landscape(id):
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    design = LandScape.get_or_404(id)

    if request.method == 'POST':
        design.design = request.form['pattern']
        design.short_desc = request.form['short_description']
        design.full_desc = request.form.get('full_description', '')

        db.session.commit()
        flash('Land Scaping updated successfully!', 'success')
        return redirect(url_for('manage_landscape'))

    return render_template(
        'admin/edit_project.html',
        design=design,
        unread_messages=unread_messages,
        current_admin=g.admin
    )








@app.route('/admin/dashboard/')
@admin_required
def admin_dashboard():
    total_projects = Project.query.count()
    total_floor = FloorStamp.query.count()
    total_design = Design.query.count()
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', projects=projects,total_floor=total_floor, total_projects=total_projects,unread_messages=unread_messages,total_design=total_design,
    current_admin=g.admin)



@app.route("/register/", methods=["GET", "POST"])
def register_admin():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    form = RegisterForm()
    if form.validate_on_submit():
        pic = form.admin_profile_pic.data
        if pic:
            filename = secure_filename(pic.filename)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = "default.jpg"
        hashed_pw = generate_password_hash(form.admin_password.data)
        new_admin = Admin(
            admin_name=form.admin_name.data,
            admin_email=form.admin_email.data,
            admin_password=hashed_pw,
            admin_profile_pic=filename,
            admin_lastlogin=datetime.utcnow()
        )
        db.session.add(new_admin)
        db.session.commit()
        flash("Admin registered successfully!", "success")
        return redirect(url_for('admin_dashboard'))  

    return render_template("admin/register.html", form=form,
    unread_messages=unread_messages, current_admin = getattr(g, 'admin', None))



@app.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        admin = Admin.query.filter_by(admin_email=email).first()

        if admin and check_password_hash(admin.admin_password, password):
            session["admin_id"] = admin.admin_id
            session["admin_name"] = admin.admin_name  
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))  

        flash("Invalid email or password!", "danger")

    return render_template("admin/login.html" ,
    unread_messages=unread_messages)


@app.route("/admin/logout/")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_name", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_login"))




def generate_reset_token(email, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='admin-password-reset')

def verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='admin-password-reset', max_age=max_age)
    except Exception:
        return None
    return email




@app.route('/admin/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    
    if request.method == 'POST':
        email = request.form.get('email')
        admin = Admin.query.filter_by(admin_email=email).first()
        
        if admin:
            token = generate_reset_token(admin.admin_email)
            reset_url = url_for('reset_password', token=token, _external=True)

            
            email_msg = EmailMessage(
                subject="Password Reset Request",
                from_email="support@ecosunsolarpower.com",
                to=[admin.admin_email],
                body=f'''Hello {admin.admin_name},

To reset your password, click the link below:
{reset_url}

If you did not request this, please ignore this email.
'''
            )
            try:
                email_msg.send()  
                flash('A password reset link has been sent to your email.', 'info')
            except Exception as e:
                flash('Failed to send reset email. Please try again later.', 'danger')
            
            return redirect(url_for('admin_login'))
        else:
            flash('Email not found.', 'danger')

    return render_template('admin/forgot_password.html', unread_messages=unread_messages)




@app.route('/admin/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('The password reset link is invalid or has expired.', 'warning')
        return redirect(url_for('forgot_password'))

    admin = Admin.query.filter_by(admin_email=email).first()
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("Passwords do not match.", 'danger')
        else:
            admin.admin_password = generate_password_hash(new_password)
            db.session.commit()
            flash("Your password has been updated.", 'success')
            return redirect(url_for('admin_login'))

    return render_template('admin/reset_password.html', token=token )









# @app.route('/admin/messages/reply/', methods=['POST'])
# def reply_message():
#     """Send a reply via email."""
#     email = request.form.get('email')
#     subject = request.form.get('subject')
#     content = request.form.get('content')

#     if not email or not content:
#         flash('Email and message content are required', 'danger')
#         return redirect(url_for('manage_messages'))

#     try:
#         msg = EmailMessage(
#             subject=f"RE: {subject}",
#             body=content,
#             to=[email]
#         )
#         msg.send()
#         flash('Reply sent successfully', 'success')
#     except Exception as e:
#         flash(f'Error sending email: {str(e)}', 'danger')

#     return redirect(url_for('manage_messages'))





# @app.route('/admin/send-mail/', methods=['GET', 'POST'])
# def send_mail():
#     """Allow admin to send emails to users."""
#     if request.method == 'POST':
#         recipient = request.form.get('recipient')
#         subject = request.form.get('subject')
#         message = request.form.get('message')

#         if not recipient or not subject or not message:
#             flash('All fields are required', 'danger')
#             return redirect(url_for('send_mail'))

#         try:
#             email = EmailMessage(subject, message, to=[recipient])
#             email.send()
#             flash('Email sent successfully!', 'success')
#         except Exception as e:
#             flash(f'Error sending email: {str(e)}', 'danger')

#         return redirect(url_for('send_mail'))

#     return render_template('admin/send_mail.html', current_admin=g.admin)


@app.route("/admin/settings/", methods=["GET", "POST"])
@admin_required
def admin_settings():
    unread_messages = ContactUs.query.filter_by(status="unread").count()
    if not g.admin:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        g.admin.admin_name = request.form["admin_name"]
        g.admin.admin_email = request.form["admin_email"]
        new_password = request.form.get("new_password")

        if new_password:
            g.admin.admin_password = generate_password_hash(new_password)

        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join("static/images", filename)
                file.save(filepath)
                g.admin.admin_profile_pic = filename
                session["admin_profile_pic"] = filename

        db.session.commit()
        session["admin_name"] = g.admin.admin_name
        flash("Settings updated successfully.", "success")
        return redirect(url_for("admin_settings"))

    return render_template("admin/settings.html",current_admin=g.admin, 
                           unread_messages=unread_messages)





# contact us messages
@app.route('/admin/messages/')
@admin_required
def manage_messages():
    search_query = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = ContactUs.query
    if search_query:
        query = query.filter(ContactUs.name.ilike(f"%{search_query}%"))

    messages_paginated = query.order_by(ContactUs.date.desc()).paginate(page=page, per_page=per_page)
    unread_messages = ContactUs.query.filter_by(status='unread').count()
    message = None  

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        html = render_template('admin/messages_table.html', messages=messages_paginated)
        return jsonify({"html": html})

    return render_template(
        'admin/manage_messages.html', 
        messages=messages_paginated,
        unread_messages=unread_messages, 
        search_query=search_query,
        message=message,
        current_admin=g.admin
    )



@app.route('/admin/messages/delete/<int:message_id>/', methods=['DELETE'])
@admin_required
def delete_message(message_id):
    """Delete a contact message using a GET request."""
    message = ContactUs.query.get_or_404(message_id)
    
    db.session.delete(message)
    db.session.commit()

    flash('Message deleted successfully', 'success')
    return redirect(url_for('manage_messages'))





# @app.route('/admin/messages/reply/', methods=['POST'])
# @admin_required
# def reply_message():
#     """Send a reply via email."""
#     email = request.form.get('email')
#     subject = request.form.get('subject')
#     content = request.form.get('content')

#     if not email or not content or not subject:
#         flash('Email, subject, and message content are required', 'danger')
#         return redirect(url_for('manage_messages'))

#     try:
#         msg = EmailMessage(
#             subject=f"RE: {subject}",
#             body=content,
#             to=[email]
#         )
#         msg.send()
#         flash('Reply sent successfully', 'success')
#     except Exception as e:
#         flash(f'Error sending email: {str(e)}', 'danger')

#     return redirect(url_for('manage_messages'))




@app.route('/admin/messages/reply/', methods=['POST'])
@admin_required
def reply_message():
    """Send a reply via email using Flask-Mail and mark the message as read."""

    print("📩 Incoming request to /admin/messages/reply/")
    print("Request method:", request.method)
    print("Headers:", dict(request.headers))
    print("Form data:", request.form.to_dict())

    message_id = request.form.get('id')
    email = request.form.get('email')
    subject = request.form.get('subject')
    content = request.form.get('content')

    print("Parsed values →")
    print(f"message_id: {message_id}")
    print(f"email: {email}")
    print(f"subject: {subject}")
    print(f"content: {content}")

    if not email or not content:
        print("❌ Missing email or content.")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Email and message content are required'}), 400
        flash('Email and message content are required', 'danger')
        return redirect(url_for('manage_messages'))

    try:
        # Create and send email with Flask-Mail
        msg = Message(
            subject=f"RE: {subject}",
            recipients=[email],
            body=content
        )
        mail.send(msg)
        print("✅ Email sent successfully.")

        # Mark the message as read
        if message_id:
            message = ContactUs.query.get(message_id)
            if message and message.status == 'unread':
                message.status = 'read'
                db.session.commit()
                print(f"✅ Message {message_id} marked as read.")

        # Get updated unread count
        unread_count = ContactUs.query.filter_by(status='unread').count()
        print("Unread count:", unread_count)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'success', 'unread_count': unread_count})

        flash('Reply sent successfully', 'success')

    except Exception as e:
        print("❌ Error sending email:", str(e))
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': f'Error sending email: {str(e)}'}), 500
        flash(f'Error sending email: {str(e)}', 'danger')

    return redirect(url_for('manage_messages'))





# @app.route('/admin/messages/reply/', methods=['POST'])
# @admin_required
# def reply_message():
#     """Send a reply via email."""
#     email = request.form.get('email')
#     subject = request.form.get('subject')
#     content = request.form.get('content')

#     if not email or not content:
#         flash('Email and message content are required', 'danger')
#         return redirect(url_for('manage_messages'))

#     try:
#         msg = EmailMessage(
#             subject=f"RE: {subject}",
#             body=content,
#             to=[email]
#         )
#         msg.send()
#         flash('Reply sent successfully', 'success')
#     except Exception as e:
#         flash(f'Error sending email: {str(e)}', 'danger')

#     return redirect(url_for('manage_messages'))




@app.route('/admin/send-mail/', methods=['GET', 'POST'])
@admin_required
def send_mail():
    """Allow admin to send emails to users."""
    if request.method == 'POST':
        recipient = request.form.get('recipient')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not recipient or not subject or not message:
            flash('All fields are required', 'danger')
            return redirect(url_for('send_mail'))

        try:
            email = EmailMessage(subject, message, to=[recipient])
            email.send()
            flash('Email sent successfully!', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')

        return redirect(url_for('send_mail'))

    return render_template('admin/send_mail.html', current_admin=g.admin)





@app.route("/admin/team/add", methods=["GET", "POST"])
@admin_required
def add_team_member():
    unread_messages = ContactUs.query.filter_by(status='unread').count()

    if request.method == "POST":
        name = request.form.get("name")
        position = request.form.get("position")
        description = request.form.get("description")
        image_file = request.files.get("image")

        if not name or not position or not image_file:
            flash("Name, position, and image are required!", "danger")
            return redirect(request.url)

        if not allowed_file(image_file.filename):
            flash("Invalid file type! Only JPG, JPEG, and PNG are allowed.", "danger")
            return redirect(request.url)

        # Secure the filename
        image_filename = secure_filename(image_file.filename)

        # Store inside UPLOAD_FOLDER/team
        team_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'team')
        os.makedirs(team_folder, exist_ok=True)  # Create folder if it doesn't exist

        image_path = os.path.join(team_folder, image_filename)
        image_file.save(image_path)

        # Save to DB
        new_member = Team(
            name=name,
            position=position,
            description=description,
            image=image_filename
        )
        db.session.add(new_member)
        db.session.commit()

        flash("Team member added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin/add_team.html",
        current_admin=g.admin,
        unread_messages=unread_messages
    )



@app.route("/admin/team")
def list_team_members():
    unread_messages = ContactUs.query.filter_by(status='unread').count()
    members = Team.query.all()
    return render_template("admin/list_team.html", members=members, current_admin=g.admin,
        unread_messages=unread_messages)



@app.route("/admin/team/delete/<int:id>", methods=["DELETE"])
@admin_required
def delete_staff(id):
    member = Team.query.get_or_404(id)

    if member.image and member.image != "default.jpg":
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'team', member.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(member)
    db.session.commit()
    flash(f"Team member '{member.name}' deleted successfully!", "success")

    return redirect(url_for("admin_dashboard"))



@app.route("/admin/team/update/<int:id>", methods=["GET", "POST"])
@admin_required
def update_team(id):
    unread_messages = ContactUs.query.filter_by(status='unread').count()
    member = Team.query.get_or_404(id)

    if request.method == "POST":
        member.name = request.form.get("name")
        member.position = request.form.get("position")
        member.description = request.form.get("description")

        image_file = request.files.get("image")
        if image_file and allowed_file(image_file.filename):
            # Delete old image if not default
            if member.image and member.image != "default.jpg":
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'team', member.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Save new image
            image_filename = secure_filename(image_file.filename)
            team_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'team')
            os.makedirs(team_folder, exist_ok=True)
            image_path = os.path.join(team_folder, image_filename)
            image_file.save(image_path)

            member.image = image_filename

        db.session.commit()
        flash("Team member updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin/update_team.html",
        member=member,
        current_admin=g.admin,
        unread_messages=unread_messages
    )
