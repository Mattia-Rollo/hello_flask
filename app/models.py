from app import db, login_manager
from app import bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer, nullable=False, default=1000)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    # Relazione per i prodotti posseduti (comprati)
    items = db.relationship("Item", foreign_keys="Item.owner", backref="owned_user", lazy=True)
    # Relazione per i prodotti creati (aggiunti al marketplace)
    created_items = db.relationship("Item", foreign_keys="Item.created_by", backref="creator_user", lazy=True)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f"{str(self.budget)[:-3]},{str(self.budget)[-3:]}$"
        else:
            return f"{self.budget}$"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def check_password_correction(self, attempted_password):
        if bcrypt.check_password_hash(self.password_hash, attempted_password):
            return True
    
    def can_access_admin(self):
        """Controlla se l'utente può accedere alle funzioni admin"""
        return self.is_admin and not self.is_banned
    
    def ban_user(self):
        """Banna l'utente"""
        self.is_banned = True
        
    def unban_user(self):
        """Sbanna l'utente"""
        self.is_banned = False


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=False)
    category = db.Column(db.String(length=50), nullable=False, default="Generale")
    condition = db.Column(db.String(length=20), nullable=False, default="Nuovo")
    weight = db.Column(db.Float, nullable=True)  # peso in kg
    image_filename = db.Column(db.String(length=100), nullable=True)  # nome file immagine
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    views = db.Column(db.Integer, nullable=False, default=0)
    owner = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Item {self.name}"
    
    def get_creator(self):
        """Restituisce l'utente che ha creato il prodotto"""
        return self.creator_user
    
    def increment_views(self):
        """Incrementa il numero di visualizzazioni"""
        self.views += 1
        db.session.commit()
    
    @property
    def formatted_created_at(self):
        """Data di creazione formattata"""
        return self.created_at.strftime("%d/%m/%Y")
    
    @property
    def formatted_weight(self):
        """Peso formattato"""
        if self.weight:
            if self.weight < 1:
                return f"{int(self.weight * 1000)}g"
            else:
                return f"{self.weight:.1f}kg"
        return "Non specificato"
    
    @property
    def image_url(self):
        """URL dell'immagine del prodotto"""
        if self.image_filename:
            return f"/static/uploads/products/{self.image_filename}"
        else:
            return "/static/images/product-placeholder.svg"
    
    @property
    def has_image(self):
        """Controlla se il prodotto ha un'immagine"""
        return self.image_filename is not None
