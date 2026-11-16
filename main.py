import sys
import json
import hashlib
import os
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QStackedWidget, 
                             QMessageBox, QScrollArea, QFrame, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

USERS_FILE = 'users.json'
MOVIES_FILE = 'movies.json'

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

def load_movies():
    if not os.path.exists(MOVIES_FILE):
        default_movies = [
            {"id": 1, "title": "Inception", "genre": "Sci-Fi", "year": 2010},
            {"id": 2, "title": "The Matrix", "genre": "Sci-Fi", "year": 1999},
            {"id": 3, "title": "Interstellar", "genre": "Sci-Fi", "year": 2014},
            {"id": 4, "title": "The Dark Knight", "genre": "Action", "year": 2008},
            {"id": 5, "title": "Pulp Fiction", "genre": "Crime", "year": 1994},
            {"id": 6, "title": "Fight Club", "genre": "Drama", "year": 1999}
        ]
        with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_movies, f, indent=4)
        return default_movies
        
    with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def get_user_preferences(username):
    users = load_users()
    if username in users:
        return users[username].get("favorites", []), users[username].get("unfavorites", [])
    return [], []

def get_recommendations(target_username):
    users = load_users()
    movies = load_movies()
    
    if target_username not in users:
        return []
        
    target_data = users[target_username]
    target_favs = set(target_data.get("favorites", []))
    target_unfavs = set(target_data.get("unfavorites", []))
    
    if not target_favs and not target_unfavs:
        return []
        
    movie_ids = [m["id"] for m in movies]
    
    def build_vector(username):
        vec = []
        u_favs = set(users[username].get("favorites", []))
        u_unfavs = set(users[username].get("unfavorites", []))
        for mid in movie_ids:
            if mid in u_favs:
                vec.append(1)
            elif mid in u_unfavs:
                vec.append(-1)
            else:
                vec.append(0)
        return vec

    target_vec = build_vector(target_username)
    
    def cosine_similarity(v1, v2):
        dot_product = sum(x * y for x, y in zip(v1, v2))
        norm1 = math.sqrt(sum(x * x for x in v1))
        norm2 = math.sqrt(sum(x * x for x in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    similarities = {}
    for user, data in users.items():
        if user == target_username:
            continue
        user_vec = build_vector(user)
        sim = cosine_similarity(target_vec, user_vec)
        if sim > 0:
            similarities[user] = sim

    if not similarities:
        return []

    recommendations_scores = []
    for mid in movie_ids:
        if mid in target_favs or mid in target_unfavs:
            continue
            
        score_numerator = 0.0
        score_denominator = 0.0
        
        for user, sim in similarities.items():
            u_favs = set(users[user].get("favorites", []))
            u_unfavs = set(users[user].get("unfavorites", []))
            
            if mid in u_favs:
                score_numerator += sim * 1
                score_denominator += sim
            elif mid in u_unfavs:
                score_numerator += sim * (-1)
                score_denominator += sim
                
        if score_denominator > 0 and score_numerator > 0:
            predicted_score = score_numerator / score_denominator
            recommendations_scores.append((mid, predicted_score))
            
    recommendations_scores.sort(key=lambda x: x[1], reverse=True)
    
    recommended_movies = []
    for mid, score in recommendations_scores:
        movie_obj = next((m for m in movies if m["id"] == mid), None)
        if movie_obj:
            recommended_movies.append({
                "movie": movie_obj,
                "score": round(score * 100, 2)
            })
            
    return recommended_movies

class MovieApp(QWidget):
    def _init_(self):
        super()._init_()
        self.current_user = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Recomandări Filme")
        self.resize(700, 800)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4; font-family: Arial;")
        
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
        title.setFont(QFont("Arial", 28, QFont.Bold))
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
        
        header_layout = QHBoxLayout()
        self.welcome_label = QLabel("Salut!")
        self.welcome_label.setFont(QFont("Arial", 18, QFont.Bold))
        
        logout_btn = QPushButton("Deconectare")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("padding: 8px 16px; background-color: #f38ba8; color: #11111b; border-radius: 6px; font-weight: bold;")
        logout_btn.clicked.connect(self.handle_logout)
        
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(10)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { background: #313244; color: #cdd6f4; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #89b4fa; color: #11111b; font-weight: bold; }
            QTabWidget::pane { border: 1px solid #45475a; }
        """)
        
        self.tab_all_movies = QWidget()
        self.tab_all_layout = QVBoxLayout()
        self.scroll_all = QScrollArea()
        self.scroll_all.setWidgetResizable(True)
        self.scroll_all.setStyleSheet("border: none; background-color: transparent;")
        self.movies_container = QWidget()
        self.movies_layout = QVBoxLayout()
        self.movies_container.setLayout(self.movies_layout)
        self.scroll_all.setWidget(self.movies_container)
        self.tab_all_layout.addWidget(self.scroll_all)
        self.tab_all_movies.setLayout(self.tab_all_layout)
        
        self.tab_recommendations = QWidget()
        self.tab_rec_layout = QVBoxLayout()
        self.scroll_rec = QScrollArea()
        self.scroll_rec.setWidgetResizable(True)
        self.scroll_rec.setStyleSheet("border: none; background-color: transparent;")
        self.recs_container = QWidget()
        self.recs_layout = QVBoxLayout()
        self.recs_container.setLayout(self.recs_layout)
        self.scroll_rec.setWidget(self.recs_container)
        self.tab_rec_layout.addWidget(self.scroll_rec)
        self.tab_recommendations.setLayout(self.tab_rec_layout)
        
        self.tabs.addTab(self.tab_all_movies, "Toate Filmele")
        self.tabs.addTab(self.tab_recommendations, "Recomandări pentru Tine")
        
        self.main_layout.addWidget(self.tabs)
        widget.setLayout(self.main_layout)
        return widget

    def handle_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        if verify_user(user, pwd):
            self.current_user = user
            self.load_ui_data()
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

    def load_ui_data(self):
        self.welcome_label.setText(f"Salut, {self.current_user}! 🍿")
        self.load_all_movies()
        self.load_recommendations()

    def load_all_movies(self):
        for i in reversed(range(self.movies_layout.count())): 
            widget_to_remove = self.movies_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
            
        movies = load_movies()
        favs, unfavs = get_user_preferences(self.current_user)
        
        for movie in movies:
            card = self.create_movie_card(movie, favs, unfavs)
            self.movies_layout.addWidget(card)
            
        self.movies_layout.addStretch()

    def load_recommendations(self):
        for i in reversed(range(self.recs_layout.count())): 
            widget_to_remove = self.recs_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
                
        recs = get_recommendations(self.current_user)
        favs, unfavs = get_user_preferences(self.current_user)
        
        if not recs:
            no_rec_lbl = QLabel("Nu avem suficiente date pentru a genera recomandări.\nEvaluează mai multe filme sau așteaptă ca alți utilizatori să își salveze preferințele.")
            no_rec_lbl.setStyleSheet("color: #a6adc8; font-size: 14px;")
            no_rec_lbl.setAlignment(Qt.AlignCenter)
            self.recs_layout.addWidget(no_rec_lbl)
        else:
            for item in recs:
                movie = item["movie"]
                score = item["score"]
                card = self.create_movie_card(movie, favs, unfavs, score)
                self.recs_layout.addWidget(card)
                
        self.recs_layout.addStretch()

    def create_movie_card(self, movie, favs, unfavs, score=None):
        card = QFrame()
        card.setStyleSheet("background-color: #313244; border-radius: 10px; margin-bottom: 10px;")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        title_text = f"{movie['title']} ({movie['year']})"
        if score is not None:
            title_text += f" - Relevanță: {score}% ⭐"
            
        title_lbl = QLabel(title_text)
        title_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        if score is not None:
            title_lbl.setStyleSheet("color: #f9e2af;")
        
        genre_lbl = QLabel(f"Gen: {movie['genre']}")
        genre_lbl.setStyleSheet("color: #a6adc8; font-size: 14px;")
        
        btn_layout = QHBoxLayout()
        fav_btn = QPushButton("❤️ Adaugă la Favorite")
        unfav_btn = QPushButton("👎 Nu îmi place")
        fav_btn.setCursor(Qt.PointingHandCursor)
        unfav_btn.setCursor(Qt.PointingHandCursor)
        
        if movie['id'] in favs:
            fav_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; padding: 8px; border-radius: 5px; font-weight: bold;")
        else:
            fav_btn.setStyleSheet("background-color: #45475a; padding: 8px; border-radius: 5px;")
            
        if movie['id'] in unfavs:
            unfav_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; padding: 8px; border-radius: 5px; font-weight: bold;")
        else:
            unfav_btn.setStyleSheet("background-color: #45475a; padding: 8px; border-radius: 5px;")
        
        fav_btn.clicked.connect(lambda checked, m_id=movie['id']: self.set_preference(m_id, 'favorite'))
        unfav_btn.clicked.connect(lambda checked, m_id=movie['id']: self.set_preference(m_id, 'unfavorite'))
        
        btn_layout.addWidget(fav_btn)
        btn_layout.addWidget(unfav_btn)
        
        card_layout.addWidget(title_lbl)
        card_layout.addWidget(genre_lbl)
        card_layout.addSpacing(10)
        card_layout.addLayout(btn_layout)
        card.setLayout(card_layout)
        return card

    def set_preference(self, movie_id, status):
        add_preference(self.current_user, movie_id, status)
        self.load_ui_data()

if _name_ == '_main_':
    app = QApplication(sys.argv)
    ex = MovieApp()
    ex.show()
    sys.exit(app.exec_())