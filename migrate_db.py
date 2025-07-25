#!/usr/bin/env python3
"""
Script per migrare il database esistente aggiungendo i nuovi campi del sistema admin
"""

from app import app, db
from app.models import User, Item

def migrate_database():
    with app.app_context():
        print("🔄 Inizio migrazione database...")
        
        try:
            # Prova a ricreare tutte le tabelle con i nuovi campi
            db.drop_all()
            db.create_all()
            print("✅ Database ricreato con nuova struttura!")
            
            # Crea un utente admin di default
            admin_user = User(
                username="admin",
                email_address="admin@flaskmarket.com",
                password="admin123",
                is_admin=True,
                budget=10000  # Budget alto per l'admin
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Utente admin creato:")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email_address}")
            print(f"   Password: admin123")
            print(f"   Budget: {admin_user.prettier_budget}")
            
            print("\n🎉 Migrazione completata con successo!")
            print("\n📋 PROSSIMI PASSI:")
            print("1. Esegui 'python populate_db.py' per aggiungere prodotti di esempio")
            print("2. Avvia l'app con 'python run.py'")
            print("3. Accedi come admin con username 'admin' e password 'admin123'")
            
        except Exception as e:
            print(f"❌ Errore durante la migrazione: {e}")
            print("Assicurati che l'app Flask non sia in esecuzione e riprova.")

if __name__ == "__main__":
    migrate_database() 