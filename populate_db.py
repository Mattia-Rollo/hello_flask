#!/usr/bin/env python3
"""
Script per popolare il database con prodotti di esempio
"""

from app import app, db
from app.models import Item, User

def populate_database():
    with app.app_context():
        # Controlla se ci sono già items nel database
        if Item.query.count() > 0:
            print("Il database contiene già degli items!")
            return
        
        # Crea un utente admin di sistema per i prodotti iniziali
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            admin_user = User(
                username="system",
                email_address="admin@flaskmarket.com", 
                password="admin123",
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # Prodotti di esempio interessanti e vari
        sample_items = [
            # Elettronica
            Item(name="iPhone 15 Pro", price=1200, barcode="123456789001", 
                 description="Ultimo modello iPhone con chip A17 Pro, fotocamera avanzata e design in titanio"),
            Item(name="MacBook Air M2", price=1399, barcode="123456789002", 
                 description="Laptop ultraleggero con chip M2, 8GB RAM, 256GB SSD. Perfetto per lavoro e studio"),
            Item(name="AirPods Pro", price=279, barcode="123456789003", 
                 description="Auricolari wireless con cancellazione del rumore attiva e audio spaziale"),
            Item(name="iPad Air", price=749, barcode="123456789004", 
                 description="Tablet versatile con display da 10.9 pollici e supporto Apple Pencil"),
            
            # Gaming
            Item(name="PlayStation 5", price=549, barcode="123456789005", 
                 description="Console next-gen con SSD ultra veloce e ray tracing in tempo reale"),
            Item(name="Nintendo Switch OLED", price=349, barcode="123456789006", 
                 description="Console ibrida con schermo OLED vibrante e dock migliorato"),
            Item(name="Xbox Series X", price=499, barcode="123456789007", 
                 description="Console 4K con backward compatibility e Xbox Game Pass"),
            
            # Casa e Lifestyle
            Item(name="Dyson V15 Detect", price=699, barcode="123456789008", 
                 description="Aspirapolvere senza fili con tecnologia laser per rilevare la polvere"),
            Item(name="Nespresso Vertuo", price=199, barcode="123456789009", 
                 description="Macchina del caffè con sistema di centrifusione e capsule grandi"),
            Item(name="Robot Roomba", price=399, barcode="123456789010", 
                 description="Robot aspirapolvere intelligente con mappatura e controllo app"),
            
            # Moda e Accessori
            Item(name="Apple Watch Ultra", price=899, barcode="123456789011", 
                 description="Smartwatch robusto per sport estremi con GPS preciso e batteria 60h"),
            Item(name="Zaino North Face", price=129, barcode="123456789012", 
                 description="Zaino tecnico impermeabile 30L per hiking e viaggi urbani"),
            Item(name="Sneakers Nike Air Max", price=159, barcode="123456789013", 
                 description="Scarpe sportive iconiche con ammortizzazione Air Max visibile"),
            
            # Sport e Fitness
            Item(name="Bicicletta Elettrica", price=1899, barcode="123456789014", 
                 description="E-bike con motore 250W, autonomia 100km e telaio in alluminio"),
            Item(name="Tapis Roulant Smart", price=599, barcode="123456789015", 
                 description="Tapis roulant pieghevole con app fitness e inclinazione automatica"),
            
            # Libri e Cultura
            Item(name="Kindle Paperwhite", price=149, barcode="123456789016", 
                 description="E-reader impermeabile con schermo da 6.8 pollici e luce regolabile"),
            Item(name="Set Lego Architecture", price=79, barcode="123456789017", 
                 description="Set da costruzione della Torre Eiffel con 649 pezzi"),
            
            # Cucina
            Item(name="Air Fryer Philips", price=199, barcode="123456789018", 
                 description="Friggitrice ad aria calda 4.1L con 7 programmi preimpostati"),
            Item(name="Multicooker Instant Pot", price=129, barcode="123456789019", 
                 description="Pentola elettrica 7-in-1: pentola a pressione, slow cooker, rice cooker"),
            
            # Prodotti economici per utenti con budget limitato
            Item(name="Powerbank Anker", price=29, barcode="123456789020", 
                 description="Batteria portatile 10000mAh con ricarica rapida USB-C"),
            Item(name="Libro Il Signore degli Anelli", price=15, barcode="123456789021", 
                 description="Trilogia completa di Tolkien in edizione economica"),
            Item(name="Tazza Smart Temperature", price=25, barcode="123456789022", 
                 description="Tazza che mantiene la temperatura perfetta del caffè per ore"),
            Item(name="Cuffie Bluetooth Basic", price=39, barcode="123456789023", 
                 description="Cuffie wireless entry-level con 20h di autonomia"),
            Item(name="Notebook Moleskine", price=19, barcode="123456789024", 
                 description="Quaderno classico a righe con copertina rigida nera")
        ]
        
        # Aggiungi tutti gli items al database con created_by e nuovi campi
        categories_mapping = {
            "iPhone": "Elettronica", "Samsung Galaxy": "Elettronica", "MacBook": "Elettronica", "Dell XPS": "Elettronica",
            "PlayStation": "Elettronica", "Nintendo": "Elettronica", "Xbox": "Elettronica",
            "Dyson": "Casa e Giardino", "Nespresso": "Casa e Giardino", "Robot": "Casa e Giardino", "Instant Pot": "Casa e Giardino",
            "Apple Watch": "Elettronica", "Zaino": "Abbigliamento", "Sneakers": "Abbigliamento",
            "Bicicletta": "Sport e Tempo Libero", "Tapis": "Sport e Tempo Libero",
            "Libro": "Libri e Riviste", "Powerbank": "Elettronica", "Tazza": "Casa e Giardino", 
            "Cuffie": "Elettronica", "Notebook": "Libri e Riviste"
        }
        
        weights_mapping = {
            "iPhone": 0.2, "Samsung": 0.19, "MacBook": 1.4, "Dell": 1.6,
            "PlayStation": 4.5, "Nintendo": 0.4, "Xbox": 4.4,
            "Dyson": 2.6, "Nespresso": 4.0, "Robot": 3.4, "Instant": 5.7,
            "Apple Watch": 0.05, "Zaino": 0.8, "Sneakers": 0.4,
            "Bicicletta": 22.0, "Tapis": 35.0,
            "Libro": 0.5, "Powerbank": 0.3, "Tazza": 0.4, "Cuffie": 0.25, "Notebook": 0.2
        }
        
        for item_data in sample_items:
            # Determina categoria e peso basandosi sul nome
            category = "Generale"
            weight = None
            
            for key, cat in categories_mapping.items():
                if key.lower() in item_data.name.lower():
                    category = cat
                    break
            
            for key, w in weights_mapping.items():
                if key.lower() in item_data.name.lower():
                    weight = w
                    break
            
            # Crea un nuovo item basato sui dati dell'item_data ma con created_by e nuovi campi
            new_item = Item(
                name=item_data.name,
                price=item_data.price,
                barcode=item_data.barcode,
                description=item_data.description,
                category=category,
                condition="Nuovo",  # Tutti i prodotti di esempio sono nuovi
                weight=weight,
                created_by=admin_user.id,
                owner=None  # Disponibile per l'acquisto
            )
            db.session.add(new_item)
        
        db.session.commit()
        print(f"✅ Aggiunti {len(sample_items)} prodotti al database!")
        
        # Statistiche
        total_items = Item.query.count()
        avg_price = db.session.query(db.func.avg(Item.price)).scalar()
        min_price = db.session.query(db.func.min(Item.price)).scalar()
        max_price = db.session.query(db.func.max(Item.price)).scalar()
        
        print(f"\n📊 STATISTICHE DATABASE:")
        print(f"   • Totale prodotti: {total_items}")
        print(f"   • Prezzo medio: ${avg_price:.2f}")
        print(f"   • Prezzo minimo: ${min_price}$") 
        print(f"   • Prezzo massimo: ${max_price}$")

if __name__ == "__main__":
    populate_database() 