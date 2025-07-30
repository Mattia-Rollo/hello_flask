#!/usr/bin/env python3
"""
Script di migrazione per aggiungere i nuovi campi al modello Item
"""

import os
import sys
from datetime import datetime

# Aggiungi il percorso dell'app al Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db
from app.models import Item, User

def migrate_database():
    """Migra il database aggiungendo i nuovi campi al modello Item"""
    
    with app.app_context():
        print("🔄 Iniziando migrazione database...")
        
        try:
            # Per SQLite, dobbiamo usare un approccio diverso
            # Aggiungiamo le colonne una per una se non esistono
            
            # Lista delle colonne da aggiungere
            columns_to_add = [
                ('category', 'VARCHAR(50) DEFAULT "Generale"'),
                ('condition', 'VARCHAR(20) DEFAULT "Nuovo"'),
                ('weight', 'FLOAT'),
                ('created_at', 'DATETIME'),  # SQLite non supporta CURRENT_TIMESTAMP in ALTER TABLE
                ('views', 'INTEGER DEFAULT 0')
            ]
            
            print("📝 Aggiungendo nuove colonne alla tabella item...")
            
            with db.engine.connect() as connection:
                for column_name, column_def in columns_to_add:
                    try:
                        # Prova ad aggiungere la colonna
                        connection.execute(db.text(f'ALTER TABLE item ADD COLUMN {column_name} {column_def}'))
                        print(f"   ✅ Aggiunta colonna: {column_name}")
                    except Exception as e:
                        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                            print(f"   ⏭️  Colonna {column_name} già esistente")
                        else:
                            print(f"   ⚠️  Errore aggiungendo {column_name}: {e}")
                
                # Ora aggiorniamo i record che potrebbero avere valori NULL
                print("🔄 Aggiornando record esistenti...")
                
                # Aggiorna i record con valori NULL
                connection.execute(db.text("""
                    UPDATE item 
                    SET category = 'Generale' 
                    WHERE category IS NULL
                """))
                
                connection.execute(db.text("""
                    UPDATE item 
                    SET condition = 'Nuovo' 
                    WHERE condition IS NULL
                """))
                
                connection.execute(db.text("""
                    UPDATE item 
                    SET views = 0 
                    WHERE views IS NULL
                """))
                
                connection.execute(db.text("""
                    UPDATE item 
                    SET created_at = CURRENT_TIMESTAMP 
                    WHERE created_at IS NULL
                """))
                
                connection.commit()
            
            print("✅ Record aggiornati")
            print("🎉 Migrazione completata con successo!")
            
        except Exception as e:
            print(f"❌ Errore durante la migrazione: {e}")
            return False
            
    return True

def verify_migration():
    """Verifica che la migrazione sia andata a buon fine"""
    
    with app.app_context():
        try:
            # Ora possiamo interrogare il database normalmente
            items_count = Item.query.count()
            
            print(f"\n📊 Verifica migrazione:")
            print(f"   Prodotti totali: {items_count}")
            
            if items_count > 0:
                # Verifica un singolo item per controllare che abbia tutti i campi
                sample_item = Item.query.first()
                print(f"   Item di esempio: {sample_item.name}")
                print(f"   - Categoria: {sample_item.category}")
                print(f"   - Condizione: {sample_item.condition}")
                print(f"   - Visualizzazioni: {sample_item.views}")
                print(f"   - Data creazione: {sample_item.created_at}")
                print(f"   - Peso: {sample_item.weight}")
                
            print("✅ Migrazione verificata con successo!")
            return True
                
        except Exception as e:
            print(f"❌ Errore durante la verifica: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Script di migrazione Flask Market - Nuovi campi prodotto")
    print("=" * 60)
    
    # Esegui migrazione
    if migrate_database():
        # Verifica migrazione
        verify_migration()
        print("\n🎯 Ora puoi avviare l'applicazione con i nuovi campi prodotto!")
        print("💡 Suggerimento: Esegui 'python3 populate_db.py' per aggiungere prodotti di esempio")
    else:
        print("\n💥 Migrazione fallita. Controlla gli errori sopra.")
        sys.exit(1) 