from flask import redirect, url_for, render_template, request, session
from sqlalchemy.exc import IntegrityError
from models import app, db, Locations, RequestLocation, UserForm
import secrets

app.secret_key = secrets.token_hex(12)
acc = {"admin":"admin"}

@app.route("/")
def home():
    return render_template("index.html")

# Adding a request to the location database
@app.route("/user_data/add/<int:request_id>")
def add_request_to_location(request_id):
    request_to_add = RequestLocation.query.get_or_404(request_id)
    new_location = Locations(
        name=request_to_add.name,
        city=request_to_add.city,
        address=request_to_add.address,
        hours=request_to_add.hours,
        link=request_to_add.link,
        phone=request_to_add.phone,
        location_type=request_to_add.location_type
    )
    db.session.add(new_location)
    db.session.delete(request_to_add)
    db.session.commit()
    return redirect(url_for("user_data"))


# Allowing user to filer and search for locations
def get_filtered_locations(city=None):
    search_query = request.args.get("search_query")
    filter_type = request.args.get("filter_type")
    query = Locations.query

    if city:
        query = query.filter_by(city=city)

    if search_query:
        search_query = f"%{search_query.lower().strip('%')}%"
        query = query.filter((Locations.name.ilike(search_query)) | (Locations.city.ilike(search_query)))
    elif filter_type:
        if filter_type == "Other":
            query = query.filter(Locations.location_type.notin_(["Cafe", "School", "Library"]))
        else:
            query = query.filter_by(location_type=filter_type)

    # Remove '%' characters from start and end of search_query for the final display.
    return query.all(), filter_type, search_query.strip('%') if search_query else search_query


@app.route("/location/vancouver")
def vancouver():
    locations, filter_type, search_query = get_filtered_locations(city="Vancouver")
    return render_template("vancouver.html", locations=locations, filter_type=filter_type, search_query=search_query)

@app.route("/location/burnaby")
def burnaby():
    locations, filter_type, search_query = get_filtered_locations(city="Burnaby")
    return render_template("burnaby.html", locations=locations, filter_type=filter_type, search_query=search_query)

@app.route("/location/surrey")
def surrey():
    locations, filter_type, search_query = get_filtered_locations(city="Surrey")
    return render_template("surrey.html", locations=locations, filter_type=filter_type, search_query=search_query)

@app.route("/location/richmond")
def richmond():
    locations, filter_type, search_query = get_filtered_locations(city="Richmond")
    return render_template("richmond.html", locations=locations, filter_type=filter_type, search_query=search_query)

@app.route("/location/coquitlam")
def coquitlam():
    locations, filter_type, search_query = get_filtered_locations(city="Coquitlam")
    return render_template("coquitlam.html", locations=locations, filter_type=filter_type, search_query=search_query)

@app.route("/locations")
def locations():
    locations, filter_type, search_query = get_filtered_locations()
    return render_template("locations.html", locations=locations, filter_type=filter_type, search_query=search_query)

@app.route("/user_data")
def user_data():
    if "admin" in session:
        requests = RequestLocation.query.all()
        return render_template("user_data.html", requests=requests)
    else:
        return redirect("login")

@app.route("/admin/edit/<int:location_id>", methods=["GET", "POST"])
def edit_location(location_id):
    if "admin" in session:
        location_to_edit = Locations.query.get_or_404(location_id)
        form = UserForm()
        # Allowing admin to edit locations
        #removed form.validate_on_submit
        if request.method == "POST":
            #Format Phone number
            phone = request.form.get("phone")
            if "-" in phone:
                processed_phone = phone
            else:
                phone_digits = [*phone]
                phone_digits.insert(3, "-")
                phone_digits.insert(7, "-")
                processed_phone = ''.join(phone_digits)

            #Format Hours of operation
            open_time = request.form.get("open")
            close_time = request.form.get("close")
            open_hours = f'{open_time} - {close_time}'

            location_to_edit.name = form.name.data
            location_to_edit.city = form.city.data
            location_to_edit.address = form.address.data
            location_to_edit.hours = open_hours
            location_to_edit.link = form.link.data
            location_to_edit.phone = processed_phone
            location_to_edit.location_type = form.location_type.data

            # Handle Integrity Error from duplicate location names/addresses added to the database.
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))
        return render_template("edit_location.html", form=form, location=location_to_edit)
    return redirect(url_for("login"))

# Allow admin to delete locations
@app.route("/admin/delete/<int:location_id>")
def delete_location(location_id):
    location_to_delete = Locations.query.get_or_404(location_id)
    db.session.delete(location_to_delete)
    db.session.commit()
    return redirect(url_for("admin"))

# Routing for deleting requests
@app.route("/user_data/delete/<int:request_id>")
def delete_request(request_id):
    request_to_delete = RequestLocation.query.get_or_404(request_id)
    db.session.delete(request_to_delete)
    db.session.commit()
    return redirect(url_for("user_data"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" in session:
        form = UserForm()
        # Allowing admin to add locations
        search_query = request.args.get("search_query")
        filter_type = request.args.get("filter_type")

        display_search_query = search_query.strip('%') if search_query else search_query

        if search_query:
            search_query = f"%{search_query.lower()}%"
            locations = Locations.query.filter(Locations.name.ilike(search_query)).all()
        elif filter_type:
            if filter_type == "Other":
                locations = Locations.query.filter(Locations.location_type.notin_(["Cafe", "School", "Library"])).all()
            else:
                locations = Locations.query.filter_by(location_type=filter_type).all()
        else:
            locations = Locations.query.all()

        return render_template("admin.html", form=form, locations=locations, filter_type=filter_type, search_query=display_search_query)
    return redirect(url_for("login"))


@app.route("/admin/new_location", methods=["GET", "POST"])
def new_location():
    if "admin" in session:
        form = UserForm()
        # Allowing admin to add locations
        #removed form.validate_on_submit
        if request.method == "POST":
            #Format Hours of operation
            open_time = request.form.get("open")
            close_time = request.form.get("close")
            open_hours = f'{open_time} - {close_time}'

            #Format Phone number
            phone = request.form.get("phone")
            if "-" in phone:
                processed_phone = phone
            else:
                phone_digits = [*phone]
                phone_digits.insert(3, "-")
                phone_digits.insert(7, "-")
                processed_phone = ''.join(phone_digits)

            name = form.name.data
            city = form.city.data
            address = form.address.data
            link = form.link.data
            location_type = form.location_type.data
            
            new_location = Locations(name=name, city=city, address=address, hours=open_hours, link=link, phone=processed_phone, location_type=location_type)
            db.session.add(new_location)

            # Handle Integrity Error from duplicate location names/addresses added to the database.
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            return redirect(url_for("admin"))

        return render_template("new_location.html", form=form)
    return redirect(url_for("login"))

@app.route("/request-location", methods=["GET", "POST"])
def request_location():
    form = UserForm()
    if request.method == "POST":
        name = form.name.data
        city = form.city.data
        address = form.address.data
        open_time = request.form.get("open")
        close_time = request.form.get("close")
        link = form.link.data
        phone = request.form.get("phone")
        location_type = form.location_type.data

        #Format Phone number
        if "-" in phone:
            processed_phone = phone
        else:
            phone_digits = [*phone]
            phone_digits.insert(3, "-")
            phone_digits.insert(7, "-")
            processed_phone = ''.join(phone_digits)
        #Format Hours of operation
        open_hours = f'{open_time} - {close_time}'
        new_location = RequestLocation(name=name, city=city, address=address, hours=open_hours, link=link, phone=processed_phone, location_type=location_type)
        db.session.add(new_location)
        # then add user request to requests database]]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        return redirect(url_for("request_location"))

    requests = RequestLocation.query.all()

    return render_template("request.html", form=form, requests=requests)

@app.route("/login")
def login():
    # Check if admin is logged in through session cookie
    if "admin" in session:
        return redirect("admin")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def auth():
    user = request.form.get("user")
    password = request.form.get("password")
    # Verify admin login entry and create log in session
    if user in acc and password == acc[user]:
        session["admin"] = user
        return redirect("admin")
    else:
        return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    # If admin session exists, remove cookie to log out.
    if "admin" in session:
        session.pop("admin")
    return redirect("/")

# Handles page for 404 error
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)