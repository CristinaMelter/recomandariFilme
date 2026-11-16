import sys
import json
import hashlib
import os
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QStackedWidget, 
                             QMessageBox, QScrollArea, QFrame, QTabWidget, 
                             QComboBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

USERS_FILE = 'users.json'
MOVIES_FILE = 'movies.json'

# ==========================================
# 1. GESTIUNEA UTILIZATORILOR ȘI PREFERINȚELOR
# ==========================================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    users = load_users()
    if username in users:
        return False  
    
    users[username] = {
        "password": hash_password(password),
        "favorites": [],
        "unfavorites": []
    }
    save_users(users)
    return True

def verify_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return username
    return None

def get_user_preferences(username):
    users = load_users()
    if username in users:
        return users[username].get("favorites", []), users[username].get("unfavorites", [])
    return [], []

def add_preference(username, movie_id, status):
    users = load_users()
    if username in users:
        if movie_id in users[username].get("favorites", []):
            users[username]["favorites"].remove(movie_id)
        if movie_id in users[username].get("unfavorites", []):
            users[username]["unfavorites"].remove(movie_id)
        
        if status == 'favorite':
            users[username].setdefault("favorites", []).append(movie_id)
        elif status == 'unfavorite':
            users[username].setdefault("unfavorites", []).append(movie_id)
        
        save_users(users)

# ==========================================
# 2. GESTIUNEA CATALOGULUI DE FILME
# ==========================================
def load_movies():
    existing_movies = []
    if os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
            try:
                existing_movies = json.load(f)
            except:
                pass
                
    if len(existing_movies) > 100:
        return existing_movies

    raw_movie_data = [
        # Acțiune & Aventură
        ("The Dark Knight", "Acțiune", 2008), ("Inception", "Acțiune", 2010), ("The Matrix", "Acțiune", 1999), 
        ("Gladiator", "Acțiune", 2000), ("Mad Max: Fury Road", "Acțiune", 2015), ("John Wick", "Acțiune", 2014), 
        ("Die Hard", "Acțiune", 1988), ("Terminator 2: Judgment Day", "Acțiune", 1991), ("Avengers: Endgame", "Acțiune", 2019),
        ("Jurassic Park", "Aventură", 1993), ("Indiana Jones and the Raiders of the Lost Ark", "Aventură", 1981), 
        ("Pirates of the Caribbean: The Curse of the Black Pearl", "Aventură", 2003), ("Back to the Future", "Aventură", 1985),
        ("The Lord of the Rings: The Fellowship of the Ring", "Aventură", 2001), ("The Lord of the Rings: The Two Towers", "Aventură", 2002),
        ("The Lord of the Rings: The Return of the King", "Aventură", 2003), ("Spider-Man: No Way Home", "Acțiune", 2021),
        ("Léon: The Professional", "Acțiune", 1994), ("V for Vendetta", "Acțiune", 2005), ("Kill Bill: Vol. 1", "Acțiune", 2003),
        ("Kill Bill: Vol. 2", "Acțiune", 2004), ("Casino Royale", "Acțiune", 2006), ("Mission: Impossible - Fallout", "Acțiune", 2018),
        ("Logan", "Acțiune", 2017), ("Batman Begins", "Acțiune", 2005), ("The Dark Knight Rises", "Acțiune", 2012),
        ("Gladiator II", "Acțiune", 2024), ("Top Gun: Maverick", "Acțiune", 2022), ("Dune: Part Two", "Aventură", 2024),
        
        # Science-Fiction & Fantasy
        ("Interstellar", "Science-Fiction", 2014), ("Avatar", "Science-Fiction", 2009), ("Blade Runner 2049", "Science-Fiction", 2017),
        ("Dune", "Science-Fiction", 2021), ("Alien", "Science-Fiction", 1979), ("Aliens", "Science-Fiction", 1986),
        ("The Terminator", "Science-Fiction", 1984), ("Arrival", "Science-Fiction", 2016), ("The Martian", "Science-Fiction", 2015),
        ("Ex Machina", "Science-Fiction", 2014), ("Star Wars: Episode IV - A New Hope", "Science-Fiction", 1977),
        ("Star Wars: Episode V - The Empire Strikes Back", "Science-Fiction", 1980), ("Gravity", "Science-Fiction", 2013),
        ("Harry Potter and the Sorcerer's Stone", "Fantasy", 2001), ("Harry Potter and the Deathly Hallows: Part 2", "Fantasy", 2011),
        ("Pan's Labyrinth", "Fantasy", 2006), ("The Hobbit: An Unexpected Journey", "Fantasy", 2012), ("Avatar: The Way of Water", "Science-Fiction", 2022),
        
        # Dramă
        ("The Shawshank Redemption", "Dramă", 1994), ("Forrest Gump", "Dramă", 1994), ("Fight Club", "Dramă", 1999),
        ("The Godfather", "Dramă", 1972), ("The Godfather: Part II", "Dramă", 1974), ("Schindler's List", "Dramă", 1993),
        ("Joker", "Dramă", 2019), ("The Green Mile", "Dramă", 1999), ("12 Angry Men", "Dramă", 1957),
        ("Good Will Hunting", "Dramă", 1997), ("Requiem for a Dream", "Dramă", 2000), ("American Beauty", "Dramă", 1999),
        ("A Beautiful Mind", "Dramă", 2001), ("The Pursuit of Happyness", "Dramă", 2006), ("There Will Be Blood", "Dramă", 2007),
        ("No Country for Old Men", "Dramă", 2007), ("Gran Torino", "Dramă", 2008), ("Dead Poets Society", "Dramă", 1989),
        ("Catch Me If You Can", "Dramă", 2002), ("The Truman Show", "Dramă", 1998), ("Rocky", "Dramă", 1976),
        ("Braveheart", "Dramă", 1995), ("Million Dollar Baby", "Dramă", 2004), ("Slumdog Millionaire", "Dramă", 2008),
        ("Whiplash", "Dramă", 2014), ("The Departed", "Dramă", 2006),
        
        # Thriller, Mister & Crimă
        ("Pulp Fiction", "Crimă", 1994), ("Se7en", "Thriller", 1995), ("The Silence of the Lambs", "Thriller", 1991),
        ("The Prestige", "Mister", 2006), ("Shutter Island", "Mister", 2010), ("Gone Girl", "Mister", 2014),
        ("Knives Out", "Mister", 2019), ("Parasite", "Thriller", 2019), ("Prisoners", "Thriller", 2013),
        ("Zodiac", "Mister", 2007), ("Goodfellas", "Crimă", 1990), ("The Usual Suspects", "Mister", 1995), 
        ("Memento", "Mister", 2000), ("Scarface", "Crimă", 1983), ("Reservoir Dogs", "Crimă", 1992), 
        ("Fargo", "Crimă", 1996), ("Nightcrawler", "Thriller", 2014), ("Snatch", "Crimă", 2000), 
        ("Heat", "Crimă", 1995), ("L.A. Confidential", "Mister", 1997), ("Sicario", "Thriller", 2015), 
        ("The Sixth Sense", "Mister", 1999), ("Mystic River", "Mister", 2003), ("Glass Onion", "Mister", 2022),
        
        # Horror & Psihologic
        ("The Shining", "Horror", 1980), ("Psycho", "Horror", 1960), ("The Conjuring", "Horror", 2013),
        ("The Exorcist", "Horror", 1973), ("Halloween", "Horror", 1978), ("A Nightmare on Elm Street", "Horror", 1984),
        ("Hereditary", "Horror", 2018), ("Get Out", "Psihologic", 2017), ("Black Swan", "Psihologic", 2010),
        ("Split", "Psihologic", 2016), ("Donnie Darko", "Psihologic", 2001), ("A Clockwork Orange", "Psihologic", 1971),
        ("The Thing", "Horror", 1982), ("It", "Horror", 2017), ("Scream", "Horror", 1996),
        ("Saw", "Horror", 2004), ("The Ring", "Horror", 2002), ("Sinister", "Horror", 2012),
        ("Midsommar", "Horror", 2019), ("The Babadook", "Horror", 2014), ("A Quiet Place", "Horror", 2018),
        
        # Comedie & Romantic
        ("The Hangover", "Comedie", 2009), ("Superbad", "Comedie", 2007), ("Dumb and Dumber", "Comedie", 1994),
        ("Groundhog Day", "Comedie", 1993), ("Step Brothers", "Comedie", 2008), ("Titanic", "Romantic", 1997),
        ("Pride & Prejudice", "Romantic", 2005), ("La La Land", "Romantic", 2016), ("The Notebook", "Romantic", 2004),
        ("Casablanca", "Romantic", 1942), ("Crazy, Stupid, Love.", "Romantic", 2011), ("Silver Linings Playbook", "Romantic", 2012),
        ("500 Days of Summer", "Romantic", 2009), ("Amélie", "Romantic", 2001), ("Before Sunrise", "Romantic", 1995),
        ("The Grand Budapest Hotel", "Comedie", 2014), ("Tropic Thunder", "Comedie", 2008), ("Anchorman", "Comedie", 2004),
        ("Borat", "Comedie", 2006), ("Shaun of the Dead", "Comedie", 2004), ("Hot Fuzz", "Comedie", 2007),
        
        # Animație
        ("The Lion King", "Animație", 1994), ("Spider-Man: Into the Spider-Verse", "Animație", 2018), 
        ("Spirited Away", "Animație", 2001), ("Toy Story", "Animație", 1995), ("WALL-E", "Animație", 2008),
        ("Coco", "Animație", 2017), ("Inside Out", "Animație", 2015), ("Up", "Animație", 2009),
        ("Finding Nemo", "Animație", 2003), ("Shrek", "Animație", 2001), ("How to Train Your Dragon", "Animație", 2010),
        ("Ratatouille", "Animație", 2007), ("The Incredibles", "Animație", 2004), ("Monsters, Inc.", "Animație", 2001),
        ("Princess Mononoke", "Animație", 1997), ("My Neighbor Totoro", "Animație", 1988),
        
        # Istoric & Biografic
        ("The Wolf of Wall Street", "Biografic", 2013), ("Oppenheimer", "Biografic", 2023), 
        ("The Social Network", "Biografic", 2010), ("Bohemian Rhapsody", "Biografic", 2018), 
        ("Hacksaw Ridge", "Istoric", 2016), ("1917", "Istoric", 2019), ("Dunkirk", "Istoric", 2017),
        ("The Pianist", "Istoric", 2002), ("Apollo 13", "Biografic", 1995), ("The Imitation Game", "Biografic", 2014),
        ("The Theory of Everything", "Biografic", 2014), ("Lincoln", "Istoric", 2012), ("The King's Speech", "Istoric", 2010)
    ]
    
    extended_movies = []
    for i, (title, genre, year) in enumerate(raw_movie_data, start=1):
        extended_movies.append({
            "id": i,
            "title": title,
            "genre": genre,
            "year": year
        })
        
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(extended_movies, f, indent=4, ensure_ascii=False)
    
    return extended_movies

# ==========================================
# 3. ALGORITMUL DE RECOMANDARE COLABORATIVĂ (CORE ENGINE)
# ==========================================
def build_interaction_matrix():
    users = load_users()
    movies = load_movies()
    matrix = {}
    for username, data in users.items():
        matrix[username] = {}
        for mid in data.get("favorites", []):
            matrix[username][mid] = 1
        for mid in data.get("unfavorites", []):
            matrix[username][mid] = -1
    return matrix, users, movies

def calculate_user_similarity(target_user, other_user, interaction_matrix, min_corated=1):
    target_ratings = interaction_matrix.get(target_user, {})
    other_ratings = interaction_matrix.get(other_user, {})
    
    I_uv = set(target_ratings.keys()).intersection(set(other_ratings.keys()))
    
    if len(I_uv) < min_corated:
        return 0.0, 0, 0
        
    mean_u = sum(target_ratings[i] for i in I_uv) / len(I_uv)
    mean_v = sum(other_ratings[i] for i in I_uv) / len(I_uv)
    
    num = sum((target_ratings[i] - mean_u) * (other_ratings[i] - mean_v) for i in I_uv)
    den_u = math.sqrt(sum((target_ratings[i] - mean_u)**2 for i in I_uv))
    den_v = math.sqrt(sum((other_ratings[i] - mean_v)**2 for i in I_uv))
    
    common_favs = sum(1 for i in I_uv if target_ratings[i] == 1 and other_ratings[i] == 1)
    
    if den_u == 0 or den_v == 0:
        cos_num = sum(target_ratings[i] * other_ratings[i] for i in I_uv)
        cos_den = math.sqrt(sum(target_ratings[i]*2 for i in I_uv)) * math.sqrt(sum(other_ratings[i]*2 for i in I_uv))
        if cos_den == 0:
            return 0.0, len(I_uv), common_favs
        return cos_num / cos_den, len(I_uv), common_favs
        
    return num / (den_u * den_v), len(I_uv), common_favs

def get_nearest_neighbors(target_user, interaction_matrix, k=10):
    neighbors = []
    for other_user in interaction_matrix.keys():
        if other_user == target_user:
            continue
        sim, corated_count, common_favs = calculate_user_similarity(target_user, other_user, interaction_matrix)
        if sim > 0:
            neighbors.append({
                "username": other_user,
                "similarity": sim,
                "corated_count": corated_count,
                "common_favs": common_favs
            })
    neighbors.sort(key=lambda x: x["similarity"], reverse=True)
    return neighbors[:k]

def predict_movie_preference(target_user, movie_id, neighbors, interaction_matrix):
    num = 0.0
    den = 0.0
    
    liked_by = []
    disliked_by = []
    highest_sim = 0.0
    
    for neighbor in neighbors:
        u = neighbor["username"]
        sim = neighbor["similarity"]
        
        rating = interaction_matrix.get(u, {}).get(movie_id, 0)
        if rating != 0:
            num += sim * rating
            den += abs(sim)
            if rating == 1:
                liked_by.append(neighbor)
                if sim > highest_sim:
                    highest_sim = sim
            elif rating == -1:
                disliked_by.append(neighbor)
                
    if den == 0:
        return None
        
    raw_pred = num / den
    return {
        "raw_prediction": raw_pred,
        "presentation_score": ((raw_pred + 1) / 2) * 100,
        "neighbors_liked": len(liked_by),
        "neighbors_disliked": len(disliked_by),
        "total_evaluated": len(liked_by) + len(disliked_by),
        "highest_sim_liked": highest_sim
    }

def generate_recommendation_explanation(pred_data):
    n_liked = pred_data["neighbors_liked"]
    high_sim = round(pred_data["highest_sim_liked"] * 100, 1)
    
    if n_liked == 0:
        return "Recomandat pe baza reducerii influenței recenziilor negative în rândul utilizatorilor similari."
    elif n_liked == 1:
        return f"Acest film a fost apreciat de 1 utilizator cu preferințe asemănătoare cu ale tale. Cel mai apropiat utilizator care l-a apreciat are o similitudine de {high_sim}%."
    else:
        return f"Acest film a fost apreciat de {n_liked} utilizatori cu preferințe asemănătoare cu ale tale. Cel mai apropiat utilizator care l-a apreciat are o similitudine de {high_sim}%."

def generate_recommendations(target_user, k=10, limit=20):
    interaction_matrix, users, movies = build_interaction_matrix()
    
    if target_user not in interaction_matrix:
        return [], []
        
    target_ratings = interaction_matrix[target_user]
    neighbors = get_nearest_neighbors(target_user, interaction_matrix, k=k)
    
    if not neighbors:
        return [], []
        
    movie_dict = {m["id"]: m for m in movies}
    recommendations = []
    
    for mid in movie_dict.keys():
        if mid in target_ratings:
            continue
            
        pred_data = predict_movie_preference(target_user, mid, neighbors, interaction_matrix)
        if pred_data is None:
            continue
            
        if pred_data["raw_prediction"] > 0:
            explanation = generate_recommendation_explanation(pred_data)
            recommendations.append({
                "movie": movie_dict[mid],
                "raw_prediction": pred_data["raw_prediction"],
                "presentation_score": pred_data["presentation_score"],
                "stats": pred_data,
                "explanation": explanation
            })
            
    recommendations.sort(key=lambda x: x["raw_prediction"], reverse=True)
    return recommendations[:limit], neighbors

# ==========================================
# 4. INTERFAȚA GRAFICĂ (GUI)
# ==========================================
class MovieApp(QWidget):
    def _init_(self):
        super()._init_()
        self.current_user = None
        self.movie_card_buttons = {} 
        self.all_movies_data = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Recomandări Filme")
        self.resize(1000, 850)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', Arial;")
        
        self.layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        
        self.login_widget = self.create_login_ui()
        self.main_widget = self.create_main_ui()
        
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.main_widget)
        
        self.layout.addWidget(self.stacked_widget)
        self.setLayout(self.layout)
        
    def create_login_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("🎬 Autentificare")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nume utilizator")
        self.username_input.setStyleSheet("padding: 12px; border-radius: 6px; background: #313244; border: 1px solid #45475a; font-size: 14px;")
        self.username_input.setFixedWidth(320)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Parolă")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 12px; border-radius: 6px; background: #313244; border: 1px solid #45475a; font-size: 14px;")
        self.password_input.setFixedWidth(320)
        
        login_btn = QPushButton("Intră în cont")
        login_btn.setFixedWidth(320)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("padding: 12px; background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 6px; font-size: 14px;")
        login_btn.clicked.connect(self.handle_login)
        
        signup_btn = QPushButton("Creează cont")
        signup_btn.setFixedWidth(320)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.setStyleSheet("padding: 12px; background-color: #a6e3a1; color: #11111b; font-weight: bold; border-radius: 6px; font-size: 14px;")
        signup_btn.clicked.connect(self.handle_signup)
        
        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(self.username_input, alignment=Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        layout.addSpacing(25)
        layout.addWidget(login_btn, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(signup_btn, alignment=Qt.AlignCenter)
        
        widget.setLayout(layout)
        return widget
        
    def create_main_ui(self):
        widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # HEADER
        header_layout = QHBoxLayout()
        self.welcome_label = QLabel("Salut!")
        self.welcome_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        logout_btn = QPushButton("Deconectare")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("padding: 8px 16px; background-color: #f38ba8; color: #11111b; border-radius: 6px; font-weight: bold;")
        logout_btn.clicked.connect(self.handle_logout)
        
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(10)
        
        # TABURI
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { background: #313244; color: #cdd6f4; padding: 12px 25px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-weight: bold; font-size: 14px;}
            QTabBar::tab:selected { background: #89b4fa; color: #11111b; }
            QTabWidget::pane { border: 2px solid #45475a; border-radius: 6px; border-top-left-radius: 0; background: #1e1e2e;}
        """)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # TAB 1: CATALOG
        self.tab_catalog = QWidget()
        self.setup_catalog_tab()
        
        # TAB 2: RECOMANDĂRI SMART
        self.tab_recommendations = QWidget()
        self.setup_recommendations_tab()
        
        self.tabs.addTab(self.tab_catalog, "📚 Catalog Filme")
        self.tabs.addTab(self.tab_recommendations, "✨ Recomandări pentru Tine")
        
        self.main_layout.addWidget(self.tabs)
        widget.setLayout(self.main_layout)
        return widget

    def setup_catalog_tab(self):
        layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Caută după titlu...")
        self.search_input.setStyleSheet("padding: 8px; border-radius: 4px; background: #313244; border: 1px solid #45475a;")
        self.search_input.textChanged.connect(self.filter_catalog)
        
        self.genre_combo = QComboBox()
        self.genre_combo.setStyleSheet("padding: 8px; border-radius: 4px; background: #313244; border: 1px solid #45475a;")
        self.genre_combo.currentIndexChanged.connect(self.filter_catalog)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Implicit", "A-Z", "Z-A", "An (Nou-Vechi)", "An (Vechi-Nou)"])
        self.sort_combo.setStyleSheet("padding: 8px; border-radius: 4px; background: #313244; border: 1px solid #45475a;")
        self.sort_combo.currentIndexChanged.connect(self.filter_catalog)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Toate filmele", "Filme Favorite ❤️", "Filme Neplăcute 👎", "Neevaluate"])
        self.view_combo.setStyleSheet("padding: 8px; border-radius: 4px; background: #313244; border: 1px solid #45475a;")
        self.view_combo.currentIndexChanged.connect(self.filter_catalog)
        
        toolbar.addWidget(self.search_input, 2)
        toolbar.addWidget(self.genre_combo, 1)
        toolbar.addWidget(self.sort_combo, 1)
        toolbar.addWidget(self.view_combo, 1)
        
        layout.addLayout(toolbar)
        
        self.scroll_catalog = QScrollArea()
        self.scroll_catalog.setWidgetResizable(True)
        self.scroll_catalog.setStyleSheet("border: none; background-color: transparent;")
        
        self.catalog_container = QWidget()
        self.catalog_layout = QGridLayout()
        self.catalog_layout.setSpacing(15)
        self.catalog_layout.setAlignment(Qt.AlignTop)
        
        self.catalog_container.setLayout(self.catalog_layout)
        self.scroll_catalog.setWidget(self.catalog_container)
        
        layout.addWidget(self.scroll_catalog)
        self.tab_catalog.setLayout(layout)

    def setup_recommendations_tab(self):
        layout = QVBoxLayout()
        self.scroll_rec = QScrollArea()
        self.scroll_rec.setWidgetResizable(True)
        self.scroll_rec.setStyleSheet("border: none; background-color: transparent;")
        
        self.recs_container = QWidget()
        self.recs_layout = QVBoxLayout()
        self.recs_container.setLayout(self.recs_layout)
        self.scroll_rec.setWidget(self.recs_container)
        
        layout.addWidget(self.scroll_rec)
        self.tab_recommendations.setLayout(layout)

    # ==========================================
    # LOGICĂ EVENIMENTE & IN-PLACE UPDATES
    # ==========================================
    def handle_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        if verify_user(user, pwd):
            self.current_user = user
            self.load_initial_data()
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Eroare", "Credențiale incorecte!")

    def handle_signup(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Eroare", "Completează toate câmpurile!")
            return
        if create_user(user, pwd):
            QMessageBox.information(self, "Succes", "Cont creat! Acum te poți autentifica.")
        else:
            QMessageBox.warning(self, "Eroare", "Numele de utilizator există deja.")

    def handle_logout(self):
        self.current_user = None
        self.username_input.clear()
        self.password_input.clear()
        self.stacked_widget.setCurrentIndex(0)

    def load_initial_data(self):
        self.welcome_label.setText(f"Salut, {self.current_user}! 🍿")
        self.all_movies_data = load_movies()
        
        genres = sorted(list(set(m["genre"] for m in self.all_movies_data)))
        self.genre_combo.blockSignals(True)
        self.genre_combo.clear()
        self.genre_combo.addItem("Toate genurile")
        self.genre_combo.addItems(genres)
        self.genre_combo.blockSignals(False)
        
        self.filter_catalog()
        self.clear_layout(self.recs_layout)

    def on_tab_changed(self, index):
        if index == 1:
            self.load_recommendations()

    def set_preference(self, movie_id, status):
        add_preference(self.current_user, movie_id, status)
        favs, unfavs = get_user_preferences(self.current_user)
        
        # ACTUALIZARE FĂRĂ JUMP SCROLL
        if movie_id in self.movie_card_buttons:
            for btns in self.movie_card_buttons[movie_id]:
                fav_btn = btns['fav']
                unfav_btn = btns['unfav']
                
                if movie_id in favs:
                    fav_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; padding: 6px; border-radius: 5px; font-weight: bold;")
                else:
                    fav_btn.setStyleSheet("background-color: #45475a; padding: 6px; border-radius: 5px; color: #cdd6f4;")
                    
                if movie_id in unfavs:
                    unfav_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; padding: 6px; border-radius: 5px; font-weight: bold;")
                else:
                    unfav_btn.setStyleSheet("background-color: #45475a; padding: 6px; border-radius: 5px; color: #cdd6f4;")

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def add_separator(self, layout):
        layout.addSpacing(15)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #45475a;")
        layout.addWidget(line)
        layout.addSpacing(15)

    # ==========================================
    # RENDER CATALOG (TAB 1)
    # ==========================================
    def filter_catalog(self):
        scroll_val = self.scroll_catalog.verticalScrollBar().value()
        
        query = self.search_input.text().lower()
        genre_filter = self.genre_combo.currentText()
        sort_mode = self.sort_combo.currentText()
        view_mode = self.view_combo.currentText()
        
        favs, unfavs = get_user_preferences(self.current_user)
        
        filtered = []
        for m in self.all_movies_data:
            if query and query not in m["title"].lower():
                continue
            if genre_filter != "Toate genurile" and m["genre"] != genre_filter:
                continue
                
            if view_mode == "Filme Favorite ❤️" and m["id"] not in favs:
                continue
            if view_mode == "Filme Neplăcute 👎" and m["id"] not in unfavs:
                continue
            if view_mode == "Neevaluate" and (m["id"] in favs or m["id"] in unfavs):
                continue
                
            filtered.append(m)
            
        if sort_mode == "A-Z":
            filtered.sort(key=lambda x: x["title"])
        elif sort_mode == "Z-A":
            filtered.sort(key=lambda x: x["title"], reverse=True)
        elif sort_mode == "An (Nou-Vechi)":
            filtered.sort(key=lambda x: x["year"], reverse=True)
        elif sort_mode == "An (Vechi-Nou)":
            filtered.sort(key=lambda x: x["year"])
            
        self.render_catalog_cards(filtered, favs, unfavs)
        QTimer.singleShot(10, lambda: self.scroll_catalog.verticalScrollBar().setValue(scroll_val))

    def render_catalog_cards(self, movies_list, favs, unfavs):
        self.clear_layout(self.catalog_layout)
        self.movie_card_buttons.clear() 
        
        col, row = 0, 0
        max_cols = 2 
        
        for m in movies_list:
            card = self.create_movie_card(m, favs, unfavs)
            self.catalog_layout.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_movie_card(self, movie, favs, unfavs):
        card = QFrame()
        card.setStyleSheet("background-color: #313244; border-radius: 8px; border: 1px solid #45475a;")
        card.setMinimumHeight(130)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        
        title_lbl = QLabel(f"<b>{movie['title']}</b> ({movie['year']})")
        title_lbl.setFont(QFont("Segoe UI", 12))
        title_lbl.setStyleSheet("border: none; color: #cdd6f4;")
        title_lbl.setWordWrap(True)
        
        genre_lbl = QLabel(f"Gen: {movie['genre']}")
        genre_lbl.setStyleSheet("border: none; color: #a6adc8; font-size: 12px;")
        
        btn_layout = QHBoxLayout()
        fav_btn = QPushButton("❤️ Fav")
        unfav_btn = QPushButton("👎 Nu")
        fav_btn.setCursor(Qt.PointingHandCursor)
        unfav_btn.setCursor(Qt.PointingHandCursor)
        
        if movie['id'] in favs:
            fav_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; padding: 6px; border-radius: 5px; font-weight: bold;")
        else:
            fav_btn.setStyleSheet("background-color: #45475a; padding: 6px; border-radius: 5px; border: none; color: #cdd6f4;")
            
        if movie['id'] in unfavs:
            unfav_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; padding: 6px; border-radius: 5px; font-weight: bold;")
        else:
            unfav_btn.setStyleSheet("background-color: #45475a; padding: 6px; border-radius: 5px; border: none; color: #cdd6f4;")
            
        fav_btn.clicked.connect(lambda checked, m_id=movie['id']: self.set_preference(m_id, 'favorite'))
        unfav_btn.clicked.connect(lambda checked, m_id=movie['id']: self.set_preference(m_id, 'unfavorite'))
        
        btn_layout.addWidget(fav_btn)
        btn_layout.addWidget(unfav_btn)
        
        if movie['id'] not in self.movie_card_buttons:
            self.movie_card_buttons[movie['id']] = []
        self.movie_card_buttons[movie['id']].append({'fav': fav_btn, 'unfav': unfav_btn})
        
        layout.addWidget(title_lbl)
        layout.addWidget(genre_lbl)
        layout.addStretch()
        layout.addLayout(btn_layout)
        card.setLayout(layout)
        return card

    # ==========================================
    # RENDER RECOMANDĂRI SMART (TAB 2)
    # ==========================================
    def load_recommendations(self):
        scroll_val = self.scroll_rec.verticalScrollBar().value()
        self.clear_layout(self.recs_layout)
        
        favs, unfavs = get_user_preferences(self.current_user)
        target_evaluated = len(favs) + len(unfavs)
        users = load_users()
        total_users = len(users)
        
        if target_evaluated == 0:
            lbl = QLabel("Nu ai evaluat încă niciun film.\n\nPentru a primi recomandări, mergi în 'Catalog Filme' și marchează cu ❤️ sau 👎 filmele pe care le-ai văzut.")
            lbl.setStyleSheet("color: #a6adc8; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.recs_layout.addWidget(lbl)
            self.recs_layout.addStretch()
            return
            
        if total_users <= 1:
            lbl = QLabel("Ești singurul utilizator din sistem momentan.\n\nNu putem genera recomandări colaborative până nu interacționează și alți utilizatori.")
            lbl.setStyleSheet("color: #a6adc8; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.recs_layout.addWidget(lbl)
            self.recs_layout.addStretch()
            return
            
        recommendations, similar_users = generate_recommendations(self.current_user, k=10, limit=20)
            
        if not similar_users:
            lbl = QLabel("Nu există utilizatori cu preferințe asemănătoare cu ale tale în acest moment.\n\nEvaluează mai multe filme pentru a găsi potriviri.")
            lbl.setStyleSheet("color: #f38ba8; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.recs_layout.addWidget(lbl)
            self.recs_layout.addStretch()
            return
        
        # --- A. UTILIZATORI CU PREFERINȚE ASEMĂNĂTOARE ---
        title_a = QLabel("A. Utilizatori cu preferințe asemănătoare")
        title_a.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_a.setStyleSheet("color: #89b4fa; padding-bottom: 5px;")
        self.recs_layout.addWidget(title_a)
        
        sim_scroll = QScrollArea()
        sim_scroll.setFixedHeight(140)
        sim_scroll.setWidgetResizable(True)
        sim_scroll.setStyleSheet("background: transparent; border: none;")
        
        sim_container = QWidget()
        sim_layout = QHBoxLayout()
        sim_container.setLayout(sim_layout)
        
        for u in similar_users:
            u_card = QFrame()
            sim_val = u['similarity']
            
            if sim_val > 50:
                u_card.setStyleSheet("background-color: #313244; border: 1px solid #a6e3a1; border-radius: 6px; padding: 10px;")
            else:
                u_card.setStyleSheet("background-color: #313244; border-radius: 6px; padding: 10px;")
                
            u_card.setFixedWidth(240)
            u_vbox = QVBoxLayout()
            u_vbox.setSpacing(5)
            u_vbox.addWidget(QLabel(f"👤 <b>{u['username']}</b>"))
            
            sim_pct = QLabel(f"{round(sim_val * 100, 1)}% similitudine")
            sim_pct.setStyleSheet("color: #a6e3a1; font-weight: bold;" if sim_val > 0.5 else "color: #f9e2af; font-weight: bold;")
            u_vbox.addWidget(sim_pct)
            
            stats_lbl = QLabel(f"• Filme evaluate în comun: {u['corated_count']}\n• Preferințe comune: {u['common_favs']}")
            stats_lbl.setStyleSheet("color: #bac2de; font-size: 12px;")
            u_vbox.addWidget(stats_lbl)
            
            u_card.setLayout(u_vbox)
            sim_layout.addWidget(u_card)
            
        sim_layout.addStretch()
        sim_scroll.setWidget(sim_container)
        self.recs_layout.addWidget(sim_scroll)
            
        self.add_separator(self.recs_layout)
        
        # --- B. FILME RECOMANDATE ---
        title_b = QLabel("B. Filme recomandate pentru tine")
        title_b.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_b.setStyleSheet("color: #a6e3a1; padding-bottom: 5px;")
        self.recs_layout.addWidget(title_b)
        
        if not recommendations:
            lbl = QLabel("Utilizatorii similari ție nu au apreciat filme pe care tu să nu le fi văzut încă.")
            lbl.setStyleSheet("color: #a6adc8; font-size: 14px;")
            self.recs_layout.addWidget(lbl)
        else:
            for item in recommendations:
                card = self.create_detailed_movie_card(item["movie"], favs, unfavs, item["presentation_score"], item["stats"], item["explanation"])
                self.recs_layout.addWidget(card)
                
        self.recs_layout.addStretch()
        QTimer.singleShot(10, lambda: self.scroll_rec.verticalScrollBar().setValue(scroll_val))

    def create_detailed_movie_card(self, movie, favs, unfavs, presentation_score, stats, explanation):
        card = QFrame()
        card.setStyleSheet("background-color: #313244; border-radius: 8px; margin-bottom: 10px; border: 1px solid #89b4fa;")
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        header = QHBoxLayout()
        title_lbl = QLabel(f"<b>{movie['title']}</b> ({movie['year']})")
        title_lbl.setFont(QFont("Segoe UI", 15))
        title_lbl.setStyleSheet("border: none;")
        
        score_lbl = QLabel(f"⭐ Scor predictiv: {round(presentation_score, 1)}%")
        score_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        score_lbl.setStyleSheet("color: #f9e2af; border: none;")
        score_lbl.setAlignment(Qt.AlignRight)
        
        header.addWidget(title_lbl)
        header.addWidget(score_lbl)
        
        genre_lbl = QLabel(f"Gen: {movie['genre']} | Evaluări vecini: {stats['neighbors_liked']} pro, {stats['neighbors_disliked']} contra")
        genre_lbl.setStyleSheet("color: #bac2de; border: none;")
        
        reason_lbl = QLabel(f"💡 Motiv: {explanation}")
        reason_lbl.setStyleSheet("color: #94e2d5; font-style: italic; margin-top: 5px; border: none;")
        reason_lbl.setWordWrap(True)
        
        btn_layout = QHBoxLayout()
        fav_btn = QPushButton("❤️ Adaugă la Favorite")
        unfav_btn = QPushButton("👎 Nu îmi place")
        fav_btn.setCursor(Qt.PointingHandCursor)
        unfav_btn.setCursor(Qt.PointingHandCursor)
        
        if movie['id'] in favs:
            fav_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; padding: 6px 15px; border-radius: 5px; font-weight: bold;")
        else:
            fav_btn.setStyleSheet("background-color: #45475a; padding: 6px 15px; border-radius: 5px; border: none; color: #cdd6f4;")
            
        if movie['id'] in unfavs:
            unfav_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; padding: 6px 15px; border-radius: 5px; font-weight: bold;")
        else:
            unfav_btn.setStyleSheet("background-color: #45475a; padding: 6px 15px; border-radius: 5px; border: none; color: #cdd6f4;")
            
        fav_btn.clicked.connect(lambda checked, m_id=movie['id']: self.set_preference(m_id, 'favorite'))
        unfav_btn.clicked.connect(lambda checked, m_id=movie['id']: self.set_preference(m_id, 'unfavorite'))
        
        if movie['id'] not in self.movie_card_buttons:
            self.movie_card_buttons[movie['id']] = []
        self.movie_card_buttons[movie['id']].append({'fav': fav_btn, 'unfav': unfav_btn})
        
        btn_layout.addWidget(fav_btn)
        btn_layout.addWidget(unfav_btn)
        btn_layout.addStretch()
        
        layout.addLayout(header)
        layout.addWidget(genre_lbl)
        layout.addWidget(reason_lbl)
        layout.addSpacing(10)
        layout.addLayout(btn_layout)
        card.setLayout(layout)
        return card

if _name_ == '_main_':
    app = QApplication(sys.argv)
    ex = MovieApp()
    ex.show()
    sys.exit(app.exec_())