#!/usr/bin/env python3
"""
Script di migrazione sicuro e semplice
"""

from app import app, db
from app.models import User, Item
import os

def safe_migrate():
    with app.app_context():
        print("🔄 Inizio migrazione database...")
        
        try:
            is_production = os.environ.get('DATABASE_URL') is not None
            print(f"📍 Ambiente: {'PRODUZIONE' if is_production else 'SVILUPPO'}")
            
            # Questo comando è sicuro: crea tabelle e colonne mancanti senza eliminare dati
            db.create_all()
            print("✅ Struttura database aggiornata")
            
            # Assicurati che esista almeno un admin
            admin_exists = User.query.filter_by(is_admin=True).first()
            if not admin_exists:
                # Se siamo in produzione e ci sono utenti, promuovi il primo
                if is_production:
                    first_user = User.query.first()
                    if first_user:
                        first_user.is_admin = True
                        db.session.commit()
                        print(f"👑 Utente {first_user.username} promosso ad amministratore")
                    else:
                        # Nessun utente esistente, crea admin
                        admin_user = User(
                            username="admin",
                            email_address="admin@flaskmarket.com",
                            password="admin123",
                            is_admin=True,
                            budget=10000
                        )
                        db.session.add(admin_user)
                        db.session.commit()
                        print("👑 Amministratore creato")
                else:
                    # Ambiente sviluppo
                    admin_user = User(
                        username="admin",
                        email_address="admin@flaskmarket.com",
                        password="admin123",
                        is_admin=True,
                        budget=10000
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("👑 Amministratore creato per sviluppo")
            else:
                print(f"👑 Amministratore esistente: {admin_exists.username}")
            
            # Aggiorna gli item esistenti che non hanno created_by
            items_without_creator = Item.query.filter_by(created_by=None).all()
            if items_without_creator:
                admin_user = User.query.filter_by(is_admin=True).first()
                for item in items_without_creator:
                    item.created_by = admin_user.id
                db.session.commit()
                print(f"🔧 Aggiornati {len(items_without_creator)} prodotti senza creatore")
            
            print("🎉 Migrazione completata con successo!")
            
        except Exception as e:
            print(f"❌ Errore durante la migrazione: {e}")
            print("🔧 Tentativo di creazione tabelle di base...")
            try:
                db.create_all()
                print("✅ Tabelle create")
            except Exception as fallback_error:
                print(f"❌ Errore critico: {fallback_error}")

if __name__ == "__main__":
    safe_migrate() 