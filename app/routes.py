from app import app, db
from flask import render_template, redirect, url_for, flash, request, abort
from app.models import Item, User
from app.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, AddItemForm
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename

name = "Mattia"
surname = "Rollo"

def admin_required(f):
    """Decorator per richiedere permessi admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_access_admin():
            flash("Accesso negato: permessi amministratore richiesti.", category="danger")
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


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
            if attempted_user.is_banned:
                flash(
                    f"Il tuo account è stato sospeso. Contatta l'amministrazione.",
                    category="danger",
                )
            else:
                login_user(attempted_user)
                flash(
                    f"Benvenuto, {attempted_user.username}!",
                    category="success",
                )
                return redirect(url_for("market"))
        else:
            flash(
                f"Username e password non corrispondono! Riprova.",
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
            # Gestisci upload immagine
            image_filename = None
            if form.image.data:
                # Genera nome file sicuro e unico
                file = form.image.data
                filename = secure_filename(file.filename)
                # Aggiungi UUID per evitare conflitti
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4().hex}_{name}{ext}"
                
                # Salva il file
                upload_path = os.path.join(app.root_path, 'static', 'uploads', 'products')
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, unique_filename)
                file.save(file_path)
                image_filename = unique_filename
            
            item_to_create = Item(
                name=form.name.data,
                price=form.price.data,
                barcode=form.barcode.data,
                description=form.description.data,
                category=form.category.data,
                condition=form.condition.data,
                weight=form.weight.data,
                image_filename=image_filename,
                owner=None,  # Disponibile per l'acquisto
                created_by=current_user.id  # Chi ha creato il prodotto
            )
            db.session.add(item_to_create)
            db.session.commit()
            flash(f"Prodotto {item_to_create.name} aggiunto al market con successo!", category="success")
            return redirect(url_for('market'))
    
    # Errori ora gestiti lato client con validazione in tempo reale
    
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

# ========== ADMIN ROUTES ==========

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    """Dashboard principale per amministratori"""
    # Statistiche generali
    total_users = User.query.count()
    banned_users = User.query.filter_by(is_banned=True).count()
    total_items = Item.query.count()
    flagged_items = Item.query.filter_by(is_flagged=True).count()
    available_items = Item.query.filter_by(owner=None).count()
    
    # Utenti recenti
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    # Prodotti recenti
    recent_items = Item.query.order_by(Item.id.desc()).limit(10).all()
    
    # Prodotti flaggati
    flagged_products = Item.query.filter_by(is_flagged=True).all()
    
    return render_template("admin/dashboard.html",
                         total_users=total_users,
                         banned_users=banned_users,
                         total_items=total_items,
                         flagged_items=flagged_items,
                         available_items=available_items,
                         recent_users=recent_users,
                         recent_items=recent_items,
                         flagged_products=flagged_products)

@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    """Gestione utenti"""
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@app.route("/admin/products")
@login_required
@admin_required
def admin_products():
    """Gestione prodotti"""
    items = Item.query.all()
    return render_template("admin/products.html", items=items)

@app.route("/admin/ban_user/<int:user_id>")
@login_required
@admin_required
def ban_user(user_id):
    """Banna un utente"""
    user = User.query.get_or_404(user_id)
    
    # Non permettere di bannare altri admin
    if user.is_admin:
        flash("Non puoi bannare un altro amministratore!", category="danger")
        return redirect(url_for('admin_users'))
    
    user.ban_user()
    db.session.commit()
    flash(f"Utente {user.username} è stato bannato.", category="warning")
    return redirect(url_for('admin_users'))

@app.route("/admin/unban_user/<int:user_id>")
@login_required
@admin_required
def unban_user(user_id):
    """Sbanna un utente"""
    user = User.query.get_or_404(user_id)
    user.unban_user()
    db.session.commit()
    flash(f"Utente {user.username} è stato sbloccato.", category="success")
    return redirect(url_for('admin_users'))

@app.route("/admin/delete_item/<int:item_id>")
@login_required
@admin_required
def delete_item(item_id):
    """Rimuove un prodotto (solo admin)"""
    item = Item.query.get_or_404(item_id)
    
    # Se il prodotto è posseduto, restituisci i soldi al proprietario
    if item.owner:
        owner = User.query.get(item.owner)
        owner.budget += item.price
        flash(f"Prodotto rimosso. Rimborsati ${item.price} a {owner.username}.", category="info")
    
    db.session.delete(item)
    db.session.commit()
    flash(f"Prodotto '{item.name}' rimosso dal sistema.", category="warning")
    return redirect(url_for('admin_products'))

@app.route("/admin/flag_item/<int:item_id>")
@login_required
@admin_required
def flag_item(item_id):
    """Flagga un prodotto come inappropriato"""
    item = Item.query.get_or_404(item_id)
    item.is_flagged = True
    db.session.commit()
    flash(f"Prodotto '{item.name}' è stato flaggato per revisione.", category="warning")
    return redirect(url_for('admin_products'))

@app.route("/admin/unflag_item/<int:item_id>")
@login_required
@admin_required
def unflag_item(item_id):
    """Rimuove il flag da un prodotto"""
    item = Item.query.get_or_404(item_id)
    item.is_flagged = False
    db.session.commit()
    flash(f"Flag rimosso dal prodotto '{item.name}'.", category="success")
    return redirect(url_for('admin_products'))

@app.route("/admin/make_admin/<int:user_id>")
@login_required
@admin_required
def make_admin(user_id):
    """Promuove un utente ad amministratore"""
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f"Utente {user.username} è ora amministratore.", category="success")
    return redirect(url_for('admin_users'))

@app.route("/admin/remove_admin/<int:user_id>")
@login_required
@admin_required
def remove_admin(user_id):
    """Rimuove privilegi admin (non se stesso)"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("Non puoi rimuovere i tuoi stessi privilegi admin!", category="danger")
        return redirect(url_for('admin_users'))
    
    user.is_admin = False
    db.session.commit()
    flash(f"Privilegi admin rimossi a {user.username}.", category="warning")
    return redirect(url_for('admin_users'))

# ========== USER REPORTING SYSTEM ==========

@app.route("/report_item/<int:item_id>")
@login_required
def report_item(item_id):
    """Gli utenti possono segnalare prodotti inappropriati"""
    item = Item.query.get_or_404(item_id)
    item.is_flagged = True
    db.session.commit()
    flash(f"Prodotto '{item.name}' segnalato agli amministratori.", category="info")
    return redirect(url_for('market'))

@app.route("/product/<int:item_id>")
def product_page(item_id):
    """Pagina di dettaglio del prodotto"""
    item = Item.query.get_or_404(item_id)
    
    # Incrementa le visualizzazioni solo se non è il proprietario o il creatore
    if not current_user.is_authenticated or (current_user.id != item.owner and current_user.id != item.created_by):
        item.increment_views()
    
    # Prodotti correlati (stessa categoria, escludendo quello attuale)
    related_products = Item.query.filter(
        Item.category == item.category,
        Item.id != item.id,
        Item.owner.is_(None)  # Solo prodotti disponibili
    ).limit(4).all()
    
    # Altri prodotti dello stesso creatore
    other_products = Item.query.filter(
        Item.created_by == item.created_by,
        Item.id != item.id
    ).limit(3).all()
    
    return render_template("product.html", 
                         item=item, 
                         related_products=related_products,
                         other_products=other_products)
