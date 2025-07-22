#!/usr/bin/env python3
"""
Script per inizializzare il database in produzione
Esegui questo script dopo il deploy per creare le tabelle
"""

from app import app, db

def init_database():
    with app.app_context():
        # Crea tutte le tabelle
        db.create_all()
        print("Database inizializzato con successo!")
        
        # Puoi aggiungere qui dati di esempio se necessario
        # ad esempio:
        # from app.models import Item
        # if Item.query.count() == 0:
        #     sample_items = [
        #         Item(name="Laptop", price=1000, barcode="123456789012", description="High performance laptop"),
        #         # aggiungi altri items...
        #     ]
        #     for item in sample_items:
        #         db.session.add(item)
        #     db.session.commit()
        #     print("Dati di esempio aggiunti!")

if __name__ == "__main__":
    init_database() 