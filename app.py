from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__, template_folder=os.path.join('birds', 'templates'))

DB_PATH = os.path.join('birds', 'ptaci.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def build_query(params):
    """
    Konstruuje WHERE klauzuli a seznam hodnot ze zadaných parametrů.
    Každou podmínku přidá jen pokud je parametr vyplněn.
    
    Args:
        params: dict s filtry (z request.args)
    
    Returns:
        tuple: (where_clause, values)
    """
    conditions = []
    values = []
    
    # Filtr podle řádu
    rad = params.get('rad', '').strip()
    if rad:
        conditions.append('rad = ?')
        values.append(rad)
    
    # Filtr podle typu potravy
    typ_potravy = params.get('typ_potravy', '').strip()
    if typ_potravy:
        conditions.append('typ_potravy = ?')
        values.append(typ_potravy)
    
    # Filtr podle kontinentu
    kontinent = params.get('vyskyt_kontinent', '').strip()
    if kontinent:
        conditions.append('vyskyt_kontinent = ?')
        values.append(kontinent)
    
    # Filtr podle migrace
    migrace = params.get('migrace', '').strip()
    if migrace in ['0', '1']:
        conditions.append('migrace = ?')
        values.append(int(migrace))
    
    # Filtr podle statusu ohrožení
    status = params.get('status_ohrozeni', '').strip()
    if status:
        conditions.append('status_ohrozeni = ?')
        values.append(status)
    
    # Filtr podle minimální hmotnosti
    hmotnost_min = params.get('hmotnost_min', '').strip()
    if hmotnost_min:
        try:
            conditions.append('hmotnost_g >= ?')
            values.append(int(hmotnost_min))
        except ValueError:
            pass
    
    # Filtr podle maximální hmotnosti
    hmotnost_max = params.get('hmotnost_max', '').strip()
    if hmotnost_max:
        try:
            conditions.append('hmotnost_g <= ?')
            values.append(int(hmotnost_max))
        except ValueError:
            pass
    
    # Spojit podmínky operátorem AND
    where_clause = ' AND '.join(conditions) if conditions else ''
    
    return where_clause, values

def get_filter_options(conn):
    """
    Načte unikátní hodnoty z databáze pro dropdowny.
    
    Args:
        conn: sqlite3 připojení
    
    Returns:
        dict: klíči jsou názvy filtrů, hodnoty jsou listy unikátních hodnot
    """
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT rad FROM ptaci WHERE rad IS NOT NULL ORDER BY rad')
    rady = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT typ_potravy FROM ptaci WHERE typ_potravy IS NOT NULL ORDER BY typ_potravy')
    typ_potravy_list = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT vyskyt_kontinent FROM ptaci WHERE vyskyt_kontinent IS NOT NULL ORDER BY vyskyt_kontinent')
    kontinenty = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT status_ohrozeni FROM ptaci WHERE status_ohrozeni IS NOT NULL ORDER BY status_ohrozeni')
    statusy = [row[0] for row in cursor.fetchall()]
    
    return {
        'rady': rady,
        'typ_potravy_list': typ_potravy_list,
        'kontinenty': kontinenty,
        'statusy': statusy
    }

@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Vytvořit WHERE klauzuli
    where_clause, params = build_query(request.args)
    
    # Sestrojit SQL dotaz
    query = 'SELECT * FROM ptaci'
    if where_clause:
        query += ' WHERE ' + where_clause
    query += ' ORDER BY nazev ASC'
    
    # Spustit dotaz
    cursor.execute(query, params)
    ptaci = cursor.fetchall()
    
    # Načíst volby pro filtry
    filter_options = get_filter_options(conn)
    
    conn.close()
    
    return render_template('dashboard.html', 
                         ptaci=ptaci, 
                         rady=filter_options['rady'],
                         typ_potravy_list=filter_options['typ_potravy_list'],
                         kontinenty=filter_options['kontinenty'],
                         statusy=filter_options['statusy'],
                         filters=request.args)

if __name__ == "__main__":
    app.run(debug=True)