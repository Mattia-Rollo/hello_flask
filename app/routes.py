from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.models import Item, User
from app.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, AddItemForm
from flask_login import login_user, logout_user, current_user, login_required

name = "Mattia"
surname = "Rollo"


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html", name=name, surname=surname)


@app.route("/market", methods=['GET', 'POST'])
@login_required
def market():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()
    
    if request.method == "POST":
        # Gestione acquisto
        purchased_item = request.form.get('purchased_item')
        if purchased_item:
            p_item_object = Item.query.filter_by(name=purchased_item).first()
            if p_item_object:
                if current_user.budget >= p_item_object.price:
                    p_item_object.owner = current_user.id
                    current_user.budget -= p_item_object.price
                    db.session.commit()
                    flash(f"Congratulazioni! Hai acquistato {p_item_object.name} per {p_item_object.price}$", category="success")
                else:
                    flash(f"Saldo insufficiente per acquistare {p_item_object.name}!", category="danger")
        
        # Gestione vendita
        sold_item = request.form.get('sold_item')
        if sold_item:
            s_item_object = Item.query.filter_by(name=sold_item).first()
            if s_item_object:
                s_item_object.owner = None
                current_user.budget += s_item_object.price
                db.session.commit()
                flash(f"Congratulazioni! Hai venduto {s_item_object.name} per {s_item_object.price}$", category="success")
        
        return redirect(url_for('market'))

    # GET request
    # Mostra tutti gli items disponibili per l'acquisto (senza proprietario)
    items = Item.query.filter_by(owner=None).all()
    # Items posseduti dall'utente
    owned_items = current_user.items
    return render_template("market.html", 
                         items=items, 
                         owned_items=owned_items, 
                         purchase_form=purchase_form, 
                         sell_form=sell_form)


@app.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data,
        )
        db.session.add(user_to_create)
        db.session.commit()
        
        # Login automatico dell'utente appena registrato
        login_user(user_to_create)
        flash(f"Registrazione completata! Benvenuto {user_to_create.username}!", category="success")
        
        return redirect(url_for("market"))
    if form.errors != {}:  # if there are not errors from the validations
        for err_msg in form.errors.values():
            flash(err_msg[0], category="danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(
                f"Success! You are logged in as: {attempted_user.username}",
                category="success",
            )
            return redirect(url_for("market"))
        else:
            flash(
                f"Username and password are not match! Please try again",
                category="danger",
            )
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect("/")

@app.route("/add_item", methods=['GET', 'POST'])
@login_required  
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        # Controlla se esiste già un item con lo stesso nome o barcode
        existing_item = Item.query.filter(
            (Item.name == form.name.data) | (Item.barcode == form.barcode.data)
        ).first()
        
        if existing_item:
            flash("Esiste già un prodotto con questo nome o codice a barre!", category="danger")
        else:
            item_to_create = Item(
                name=form.name.data,
                price=form.price.data,
                barcode=form.barcode.data,
                description=form.description.data,
                owner=None  # Disponibile per l'acquisto
            )
            db.session.add(item_to_create)
            db.session.commit()
            flash(f"Prodotto {item_to_create.name} aggiunto al market con successo!", category="success")
            return redirect(url_for('market'))
    
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg[0], category="danger")
    
    return render_template("add_item.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    # Statistiche utente
    owned_items_count = len(current_user.items)
    total_value = sum(item.price for item in current_user.items)
    
    # Statistiche generali market
    available_items = Item.query.filter_by(owner=None).count()
    total_items = Item.query.count()
    
    return render_template("dashboard.html", 
                         owned_items_count=owned_items_count,
                         total_value=total_value,
                         available_items=available_items,
                         total_items=total_items)
