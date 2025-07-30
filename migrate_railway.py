#!/usr/bin/env python3
"""
Script di migrazione per Railway PostgreSQL - Campo image_filename
"""

import os
import sys

# Aggiungi il percorso dell'app al Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db
from app.models import Item, User

def migrate_railway_database():
    """Migra il database PostgreSQL su Railway aggiungendo image_filename"""
    
    with app.app_context():
        print("🚀 Migrazione Railway - Sistema Immagini")
        print("=" * 50)
        
        try:
            # Per PostgreSQL su Railway, usa ALTER TABLE se la colonna non existe
            with db.engine.connect() as connection:
                # Verifica se la colonna esiste già
                result = connection.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='item' AND column_name='image_filename'
                """))
                
                if result.fetchone():
                    print("   ⏭️  Colonna image_filename già esistente")
                else:
                    # Aggiungi la colonna
                    connection.execute(db.text(
                        'ALTER TABLE item ADD COLUMN image_filename VARCHAR(100)'
                    ))
                    print("   ✅ Aggiunta colonna: image_filename VARCHAR(100)")
                
                connection.commit()
            
            # Verifica migrazione
            items_count = Item.query.count()
            print(f"\n📊 Verifica:")
            print(f"   Prodotti totali: {items_count}")
            
            if items_count > 0:
                sample_item = Item.query.first()
                print(f"   Item esempio: {sample_item.name}")
                print(f"   - Ha immagine: {sample_item.has_image}")
                print(f"   - URL immagine: {sample_item.image_url}")
                
            print("\n🎉 Migrazione Railway completata!")
            print("💡 Il sistema immagini è ora attivo in produzione")
            
            return True
            
        except Exception as e:
            print(f"❌ Errore durante la migrazione: {e}")
            return False

if __name__ == "__main__":
    migrate_railway_database() 