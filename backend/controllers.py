#App Routes
from datetime import datetime
from flask import render_template, request, url_for, redirect, session
from sqlalchemy import or_
from .models import *
from flask import current_app as app

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/professional_reg', methods=["GET", "POST"])
def professional_reg():
    if request.method=="GET":
        services = Service.query.all()
        service_names = [service.name for service in services]
        return render_template("professional_registration.html", services=service_names)
    username=request.form["email"]
    password=request.form["password"]
    full_name=request.form["full_name"]
    service_name=request.form.get("service_name")
    experience=request.form["experience"]
    address=request.form["address"]
    pincode=request.form["pincode"]
    professional = Professional.query.filter_by(username=username).first()
    user=User.query.filter_by(username=username).first()
    if user:
        return render_template("invalid_registration.html", role="Customer")
    if professional and professional.status=="Approved":
        session['professional_login'] = True
        redirect(url_for('professional', professional_id=professional.id))
    elif professional and professional.status=="In Progress":
        return render_template("/professionals/in_progress.html")
    elif professional and professional.status=="Rejected":
        return render_template("/professionals/rejected.html")
    elif not professional:
        new_professional=Professional(
            username=username,
            password=password,
            full_name=full_name,
            service_name=service_name,
            experience=experience,
            address=address,
            pincode=pincode,
            status="In Progress"
        )
        db.session.add(new_professional)
        db.session.commit()
        session['professional_login'] = True
        return render_template("/professionals/in_progress.html")

@app.route('/user_reg', methods=["GET", "POST"])
def user_reg():
    if request.method=="GET":
        return render_template("user_registration.html")
    username=request.form["email"]
    password=request.form["password"]
    full_name=request.form["full_name"]
    address=request.form["address"]
    pincode=request.form["pincode"]
    user=User.query.filter_by(username=username).first()
    professional=Professional.query.filter_by(username=username).first()
    if professional:
        return render_template("invalid_registration.html", role="Professional")
    if user:
        session['user_login'] = True
        return redirect(url_for('user', user_id=user.id))
    else:
        new_user=User(
            username=username,
            password=password,
            full_name=full_name,
            address=address,
            pincode=pincode,
            role="customer"
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_login'] = True
        return redirect(url_for('user', user_id=new_user.id))


@app.route('/login', methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    
    admin = User.query.filter_by(username=email, role='admin').first()
    user = User.query.filter_by(username=email, role='customer').first()
    professional=Professional.query.filter_by(username=email).first()

    if admin and password == admin.password:
        session['admin_login'] = True
        return redirect('/admin')
    
    elif user and password == user.password:
        session['user_login'] = True
        return redirect(url_for('user', user_id=user.id))
    
    elif professional and password == professional.password:
        if professional.status=="Approved":
            session['professional_login'] = True
            return redirect(url_for('professional', professional_id=professional.id))
        elif professional.status=="In Progress":
            return render_template("/professionals/in_progress.html")
        elif professional.status=="Rejected":
            return render_template("/professionals/rejected.html")
    else:
        return render_template("invalid_login.html")
    
@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method=="GET":
        services = Service.query.all()
        professionals=Professional.query.all()
        service_requests=ServiceRequest.query.all()
        return render_template("admin/admin.html", services=services, professionals=professionals, service_requests=service_requests)

@app.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    # If the request is POST, process the search
    if request.method == 'POST':
        category = request.form.get("category")  # Get the selected category
        query = request.form.get("query")  
        search_results = []

        if category == 'customers':
            search_results = User.query.filter(User.full_name.ilike(f'%{query}%')).all()
        elif category == 'professionals':
            search_results = Professional.query.filter(Professional.full_name.ilike(f'%{query}%')).all()
        elif category == 'services':
            search_results = Service.query.filter(Service.name.ilike(f'%{query}%')).all()
        
        # Return the search results to the template
        return render_template("admin/search.html", category=category, search_results=search_results)
    
    return render_template("admin/search.html", search_results=[])

@app.route('/admin_summary', methods=["GET"])
def admin_summary():
    if request.method=="GET":
        return render_template("admin/summary.html")
    
@app.route('/admin_logout', methods=["GET", "POST"])
def admin_logout():
    session.pop('admin_login', None)
    return redirect('/')


@app.route('/service_view/<int:service_id>', methods=["GET"])
def service_view(service_id):
    if request.method=="GET":
        service=Service.query.filter_by(id=service_id).first()
        return render_template("/services/service_details.html", service=service)

@app.route('/service_add', methods=["GET", "POST"])
def service_add():
    if request.method=="GET":
        return render_template("services/new_service.html")
    name=request.form["name"]
    description=request.form["description"]
    base_price=request.form["base_price"]
    service=Service.query.filter_by(name=name).first()
    if service:
        return render_template("services/service_details.html", service=service)
    else:
        new_service=Service(
            name=name,
            description=description,
            base_price=base_price
        )
        db.session.add(new_service)
        db.session.commit()
        return render_template("services/service_details.html", service=new_service)

    
@app.route('/service_edit/<int:service_id>', methods=["GET", "POST"])
def service_edit(service_id):
    service=Service.query.filter_by(id=service_id).first()
    if request.method=="GET":
        return render_template("services/service_edit.html", service=service)
    service.name = request.form['name']
    service.description = request.form['description']
    service.base_price = request.form['base_price']
    db.session.commit()
    return redirect("/admin")

    
@app.route('/service_delete/<int:service_id>', methods=["GET"])
def service_delete(service_id):
    if request.method=="GET":
        service=Service.query.filter_by(id=service_id).first()
        reviews=Review.query.filter_by(service_id=service_id).all()
        service_requests=ServiceRequest.query.filter_by(service_id=service_id).all()
        for review in reviews:
            db.session.delete(review)
        for service in service_requests:
            db.session.delete(service)
        db.session.delete(service)
        db.session.commit()
        return redirect("/admin")
    
@app.route('/professional/<int:professional_id>', methods=["GET", "POST"])
def professional(professional_id):
    professional=Professional.query.filter_by(id=professional_id).first()
    if request.method=="GET":
        current_requests = ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional.id,
            or_(
                ServiceRequest.status == "Requested",
                ServiceRequest.status == "Accepted"
            )
        ).all()
        closed_requests=ServiceRequest.query.filter_by(professional_id=professional.id, status="Closed").all()
        for requests in closed_requests:
            review=Review.query.filter_by(customer_id=requests.customer_id, service_id=requests.service_id, professional_id=professional.id).first()
            requests.rating=review.rating
        return render_template("professionals/professional.html", professional=professional, current_requests=current_requests, closed_requests=closed_requests)

@app.route('/professional_view/<int:professional_id>', methods=["GET"])
def professional_view(professional_id):
    if request.method=="GET":
        professional=Professional.query.filter_by(id=professional_id).first()
        checked = request.args.get('checked', 'False') == 'True'
        return render_template("/professionals/professional_details.html", professional=professional, checked=checked)

@app.route('/approve_professional/<int:professional_id>', methods=["GET"])
def approve_professional(professional_id):
    professional=Professional.query.filter_by(id=professional_id).first()
    professional.status="Approved"
    db.session.commit()
    return redirect("/admin")

@app.route('/reject_professional/<int:professional_id>', methods=["GET"])
def reject_professional(professional_id):
    professional=Professional.query.filter_by(id=professional_id).first()
    professional.status="Rejected"
    db.session.commit()
    return redirect("/admin")

@app.route('/professional_delete/<int:professional_id>', methods=["GET"])
def professional_delete(professional_id):
    professional=Professional.query.filter_by(id=professional_id).first()
    db.session.delete(professional)
    db.session.commit()
    return redirect("/admin")

@app.route('/professional_edit/<int:professional_id>', methods=["GET", "POST"])
def professional_edit(professional_id):
    professional=Professional.query.filter_by(id=professional_id).first()
    if request.method=="GET":
        services = Service.query.all()
        service_names = [service.name for service in services]
        return render_template("professionals/professional_edit.html", professional=professional, services=service_names)
    professional.username=request.form["email"]
    professional.password=request.form["password"]
    professional.full_name=request.form["full_name"]
    professional.service_name=request.form.get("service_name")
    professional.experience=request.form["experience"]
    professional.address=request.form["address"]
    professional.pincode=request.form["pincode"]
    db.session.commit()
    return redirect(url_for('professional_view', professional_id=professional.id, checked=True))

@app.route('/professional_search/<int:professional_id>', methods=['GET', 'POST'])
def professional_search(professional_id):
    professional=Professional.query.filter_by(id=professional_id).first()
    if request.method == 'POST':
        category = request.form.get('category')
        query = request.form.get('query')
        search_results = []

        if category == 'date':
            query_date = datetime.strptime(query, "%d-%m-%Y").date()
            search_results = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                db.func.date(ServiceRequest.date_requested) == query_date
            ).all()
            
        elif category == 'location':
            search_results = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.customer.has(User.address.ilike(f'%{query}%')) 
            ).all()

        elif category == 'pincode':
            search_results = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.customer.has(User.pincode==query) 
            ).all()

        return render_template('professionals/search.html', professional=professional,professional_id=professional_id, search_results=search_results)

    return render_template('professionals/search.html', professional=professional,professional_id=professional_id, search_results=[])


@app.route('/professional_summary/<int:professional_id>', methods=["GET"])
def professional_summary(professional_id):
    if request.method=="GET":
        professional=Professional.query.filter_by(id=professional_id).first()
        return render_template("professionals/summary.html", professional=professional)
    
@app.route('/professional_logout', methods=["GET", "POST"])
def professional_logout():
    session.pop('professional_login', None)
    return redirect('/')

@app.route('/user/<int:user_id>', methods=["GET", "POST"])
def user(user_id):
    user=User.query.filter_by(id=user_id).first()
    if request.method=="GET":
        services = Service.query.all()
        service_requests=ServiceRequest.query.filter_by(customer_id=user.id).all()
        return render_template("customers/customer.html", user=user, services=services, service_requests=service_requests, general=True)
    service_id = request.form["service_id"]
    current_service=Service.query.filter_by(id=service_id).first()
    professional_list={}
    professionals=Professional.query.filter_by(service_name=current_service.name).all()
    for professional in professionals:
        reviews=Review.query.filter_by(professional_id=professional.id).all()
        if(reviews):
            rating_sum=0
            for ratings in reviews:
                rating_sum+=ratings.rating
            rating_avg=rating_sum/len(reviews)
            professional_list[professional]= rating_avg
        else:
            professional_list[professional] = "None"
    return render_template("customers/customer.html", user=user, current_service=current_service, professional_list=professional_list, general=False)
        
@app.route('/user_view/<int:user_id>', methods=["GET"])
def user_view(user_id):
    if request.method=="GET":
        user=User.query.filter_by(id=user_id).first()
        return render_template("/customers/customer_details.html", user=user)

@app.route('/user_edit/<int:user_id>', methods=["GET", "POST"])
def user_edit(user_id):
    user=User.query.filter_by(id=user_id).first()
    if request.method=="GET":
        return render_template("customers/customer_edit.html", user=user)
    user.username=request.form["email"]
    user.password=request.form["password"]
    user.full_name=request.form["full_name"]
    user.address=request.form["address"]
    user.pincode=request.form["pincode"]
    db.session.commit()
    return redirect(url_for('user_view', user_id=user.id))

@app.route('/user_search/<int:user_id>', methods=["GET", "POST"])
def user_search(user_id):
    user=User.query.filter_by(id=user_id).first()
    if request.method=="POST":
        query = request.form.get('query')
        current_service = Service.query.filter(Service.name.ilike(f"%{query}%")).first()
        if(current_service):
            professional_list={}
            professionals=Professional.query.filter_by(service_name=current_service.name).all()
            for professional in professionals:
                reviews=Review.query.filter_by(professional_id=professional.id).all()
                if(reviews):
                    rating_sum=0
                    for ratings in reviews:
                        rating_sum+=ratings.rating
                    rating_avg=rating_sum/len(reviews)
                    professional_list[professional]= rating_avg
                else:
                    professional_list[professional] = "None"
            
            return render_template('customers/search.html', user=user, current_service=current_service, checked=True, professional_list=professional_list)
        return render_template('customers/search.html', user=user, checked=False)
    
    return render_template('customers/search.html', user=user, checked=False)


@app.route('/user_summary/<int:user_id>', methods=["GET", "POST"])
def user_summary(user_id):
    if request.method=="GET":
        user=User.query.filter_by(id=user_id).first()
        return render_template("customers/summary.html", user=user)
    
@app.route('/user_logout', methods=["GET", "POST"])
def user_logout():
    session.pop('user_login', None)
    return redirect('/')

@app.route("/book/<int:user_id>/<int:professional_id>/<int:service_id>", methods=["POST"])
def book_service(user_id, professional_id, service_id):
    requests = ServiceRequest.query.filter_by(customer_id=user_id, professional_id=professional_id, service_id=service_id).first()
    if(requests):
        return render_template("services/duplicate_service.html", user_id=user_id)
    new_request = ServiceRequest(
        service_id=service_id,
        customer_id=user_id,
        professional_id=professional_id,
        status="Requested"
    )
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('user', user_id=user_id))


@app.route("/close/<int:user_id>/<int:professional_id>/<int:service_id>", methods=["GET","POST"])
def close_service(user_id, professional_id, service_id):
    requests = ServiceRequest.query.filter_by(customer_id=user_id, professional_id=professional_id, service_id=service_id).first()
    requests.status="Closed"
    requests.date_completed=db.func.current_date()
    db.session.commit()
    return render_template("/customers/rating.html", requests=requests, user_id=user_id, professional_id=professional_id, service_id=service_id)

@app.route("/accept_request/<int:professional_id>/<int:request_id>", methods=["GET","POST"])
def accept_request(professional_id, request_id):
    requests = ServiceRequest.query.filter_by(id=request_id).first()
    requests.status="Accepted"
    db.session.commit()
    return redirect(url_for('professional', professional_id=professional_id))


@app.route("/reject_request/<int:professional_id>/<int:request_id>", methods=["GET","POST"])
def reject_request(professional_id, request_id):
    requests = ServiceRequest.query.filter_by(id=request_id).first()
    requests.status="Rejected"
    db.session.commit()
    return redirect(url_for('professional', professional_id=professional_id))

@app.route("/submit-remarks/<int:user_id>/<int:professional_id>/<int:service_id>", methods=["POST"])
def submit_remarks(user_id, professional_id, service_id):
    rating = request.form.get("rate")
    remarks = request.form.get("remarks")
    review = Review(
            rating=int(rating),  
            comment=remarks,
            customer_id=user_id,  
            professional_id=professional_id,  
            service_id=service_id,  
        )
    db.session.add(review)
    db.session.commit()
    return redirect(url_for('user', user_id=user_id))