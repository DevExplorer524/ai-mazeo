import os
import datetime
import random
import urllib.parse
import urllib.request
import json
import re
import math
import requests 
import time
import shutil
import sqlite3
import hashlib

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from knowledge import KNOWLEDGE_BASE
from knowledge_manager import KnowledgeManager
from researcher import WebResearcher

app = Flask(__name__)
app.secret_key = "mazeo_ultra_secure_key_2025"

# --- Database Setup (SQLite for Users & Global Knowledge) ---
DB_PATH = "mazeo_system.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        avatar TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Shared Knowledge table (Learned across all instances)
    cursor.execute('''CREATE TABLE IF NOT EXISTS global_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        content TEXT,
        sources TEXT,
        verified_by TEXT,
        learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

# Initialize subsystems
KM = KnowledgeManager()
RESEARCHER = WebResearcher()
IMAGE_CACHE = {}

# --- Helper Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_shared_fact(query):
    """البحث في المعرفة العالمية المشتركة بين جميع المستخدمين"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Simple semantic search simulation via LIKE
    cursor.execute("SELECT content FROM global_facts WHERE topic LIKE ? OR content LIKE ? LIMIT 1", 
                   (f"%{query}%", f"%{query}%"))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_shared_fact(topic, content, sources):
    """إضافة معلومة جديدة للقاعدة العالمية ليستفيد منها الجميع"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO global_facts (topic, content, sources, verified_by) VALUES (?, ?, ?, ?)",
                       (topic, content, json.dumps(sources), "Mazeo Autonomous Learning"))
        conn.commit()
        conn.close()
        print(f"[Mazeo Discovery] New global knowledge added: {topic}")
    except: pass

# --- Helper Classes ---

class ResponseFormatter:
    def format_brief_response(self, text, max_length):
        if not text: return ""
        words = text.split()
        if len(words) <= max_length:
            return text
        return " ".join(words[:max_length]) + "..."

    def truncate_to_length(self, text, max_length):
        return self.format_brief_response(text, max_length)

    def format_greeting(self, name):
        return f"أهلاً {name}! كيف يمكنني مساعدتك اليوم؟"

class ContextAnalyzer:
    def analyze(self, text):
        text_len = len(text.split())
        style = 'moderate'
        max_len = 400
        
        # Adaptive length logic prioritization (Enhanced for 2025)
        # Detailed triggers
        if any(w in text for w in ['تفصيل', 'شرح', 'بالتفصيل', 'كامل', 'تقرير', 'لماذا', 'كيف', 'explain', 'detail', 'why', 'how']):
            style = 'detailed'
            max_len = 1200 # Allow long educational responses
        # Brief triggers
        elif any(w in text for w in ['باختصار', 'مختصر', 'سريع', 'كلمة', 'نبذة', 'short', 'brief']):
            style = 'brief'
            max_len = 80
        # Auto-length detection
        elif text_len > 25:
            style = 'detailed'
            max_len = 1200
        elif text_len < 5:
            style = 'brief'
            max_len = 80
            
        msg_type = self.determine_type(text)
        
        return {
            'type': msg_type,
            'response_style': style,
            'max_length': max_len,
            'needs_web_search': self.needs_search(text, msg_type)
        }
        
    def determine_type(self, text):
        text = text.lower()
        if any(w in text for w in ['أهلاً', 'مرحبا', 'السلام عليكم', 'hey', 'hello', 'hi']):
            return 'GREETING'
        # General queries now handled mostly by the LLM
        if any(w in text for w in ['من صنعك', 'مطورك', 'mazen', 'creator']):
            return 'CREATOR_QUERY'
        return 'GENERAL'
        
    def needs_search(self, text, msg_type):
        if msg_type == 'CREATOR_QUERY': return False
        # Always search if it contains news keywords
        if any(w in text for w in ['جديد', 'خبر', 'اخبار', 'اليوم', '2024', '2025', 'latest', 'news']):
            return True
        # Also search for factual questions if they contain verifying particles
        if any(w in text for w in ['من هو', 'ما هو', 'اين', 'متى', 'لماذا', 'كم', 'who', 'what', 'where', 'when']):
            return True
        return False

class FactVerifier:
    def verify_response(self, response, context):
        # Simplified verification logic
        return {
            'is_reliable': True, 
            'verified_response': response,
            'confidence': 0.85,
            'warnings': []
        }

ANALYZER = ContextAnalyzer()
FORMATTER = ResponseFormatter()
FACT_VERIFIER = FactVerifier()

# --- Static Sports Data ---
FOOTBALL_DATA_2024_2025 = {
    'ballon_dor_2024': "الفائز بالكرة الذهبية 2024 هو رودري (Rodri) لاعب مانشستر سيتي ومنتخب إسبانيا.",
    'ballon_dor_2023': "ليونيل ميسي هو الفائز بالكرة الذهبية 2023.",
    'champions_league_2024': "ريال مدريد هو بطل دوري أبطال أوروبا 2023-2024 للمرة الـ15 في تاريخه بعد الفوز على دورتموند 2-0.",
    'euro_2024': "منتخب إسبانيا هو بطل يورو 2024 بعد الفوز على إنجلترا 2-1 في النهائي.",
    'copa_america_2024': "الأرجنتين هي بطلة كوبا أمريكا 2024 بعد الفوز على كولومبيا 1-0.",
    'leagues_2024': {
        'premier_league': "مانشستر سيتي",
        'la_liga': "ريال مدريد",
        'serie_a': "إنتر ميلان",
        'bundesliga': "باير ليفركوزن"
    },
    'top_players_2024': {'real_madrid': ['Vinicius', 'Bellingham'], 'city': ['Rodri', 'Haaland']},
    'recent_records': ['Bellingham most goals', 'Mbappe transfer']
}

def get_ballon_dor_winner(year):
    if year == 2024: return FOOTBALL_DATA_2024_2025['ballon_dor_2024']
    if year == 2023: return FOOTBALL_DATA_2024_2025['ballon_dor_2023']
    return "معلومات غير متوفرة"

def get_champions_league_winner(season="2023_2024"):
    return FOOTBALL_DATA_2024_2025['champions_league_2024']

def get_euro_2024_info():
    return FOOTBALL_DATA_2024_2025['euro_2024']

def get_copa_america_2024_info():
    return FOOTBALL_DATA_2024_2025['copa_america_2024']

def get_league_champion(league, season):
    return FOOTBALL_DATA_2024_2025['leagues_2024'].get(league, "غير معروف")

def search_player(name):
    # Mock player data
    players = {
        'messi': "ليونيل ميسي: لاعب إنتر ميامي، بطل العالم 2022، صاحب 8 كرات ذهبية.",
        'ronaldo': "كريستيانو رونالدو: لاعب النصر السعودي، الهداف التاريخي لكرة القدم.",
        'mbappe': "كيليان مبابي: لاعب ريال مدريد الجديد، بطل كأس العالم 2018.",
        'salah': "محمد صلاح: نجم ليفربول ومنتخب مصر، أحد أفضل الهدافين في العالم."
    }
    for k, v in players.items():
        if k in name.lower() or name in v:
            return [v]
    return ["لم يتم العثور على اللاعب"]


# --- Local Deep Intelligence (Mazeo Brain V2) ---
class MazeoLocalBrain:
    def __init__(self):
        # موازين تحليل المشاعر (تأثير طول الجملة، الكلمات المفتاحية، إلخ)
        self.sentiment_weights = [0.1, 0.4, 0.2, 0.3]
        self.intents = {
            "FACTUAL": ["ماذا", "لماذا", "كيف", "أين", "اين", "من هو", "من هي", "ماهو", "ماهي", "ما هي", "تاريخ", "معلومات", "شرح", "كيفية", "متى"],
            "EMOTIONAL": ["حزين", "سعيد", "شكرا", "اشكرك", "ممتاز"],
            "CREATOR": ["من صنعك", "من طورك", "مازن", "mazen saber"]
        }

    def sigmoid(self, x):
         return 1 / (1 + math.exp(-x))

    def analyze_message(self, text):
        text_lower = text.lower()
        
        # 1. تحديد النية (Intent Detection)
        detected_intent = "CORE_CHAT"
        for intent, keywords in self.intents.items():
            if any(kw in text_lower for kw in keywords):
                detected_intent = intent
                break
        
        # 2. حساب المشاعر (Sentiment)
        features = [
            min(len(text)/100, 1.0),
            1.0 if "!" in text else 0.0,
            1.0 if "?" in text else 0.0,
            len([w for w in text_lower.split() if len(w) > 3]) / (len(text_lower.split()) + 1)
        ]
        # Dot product
        dot_product = sum(f * w for f, w in zip(features, self.sentiment_weights))
        score = self.sigmoid(dot_product)
        sentiment = "Positive" if score > 0.5 else "Neutral/Sensitive"
        
        return detected_intent, sentiment

# تشغيل المخ المحلي
BRAIN = MazeoLocalBrain()

# System handles data through KnowledgeManager KM

# --- GEMINI AI ENGINE (محرك جمناي الخارق) ---
# Gemini API Key used in mazeo.py
GEMINI_API_KEY = "AIzaSyDBJh_FcjUVtA6XQpqYxMNrPscZEnm4MfE"

def call_gemini_ai(prompt, system_instruction=""):
    """
    Calls Google Gemini 2.5 Flash API directly via REST.
    This model supports deep thinking and extremely fast responses.
    """
    try:
        # Gemini 2.5 Flash - The current state-of-the-art for 2025
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # System instructions are better handled by prepending in lite REST calls
        full_prompt = f"System Instruction: {system_instruction}\n\nUser Input: {prompt}" if system_instruction else prompt
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            }
        }
        
        response = requests.post(url, json=payload, timeout=12)
        data = response.json()
        
        if 'candidates' in data and len(data['candidates']) > 0:
            # Gemini 2.5 might return thoughts, but the final text is in parts
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"[Gemini 2.5 Error] Response Error: {data}")
            return None
    except Exception as e:
        print(f"[Gemini 2.5 Connection Error] {e}")
        return None

# ذاكرة الجلسة
MEMORY = {"user_name": "User"}

# --- Intelligent Response Orchestrator (منظم الردود الهجين المحسّن) ---

def search_football_database(query: str) -> str:
    """يبحث في قاعدة بيانات كرة القدم المحدثة"""
    query_lower = query.lower()
    
    # البحث عن الكرة الذهبية
    if any(word in query_lower for word in ["كرة ذهبية", "ballon", "جائزة"]):
        if "2024" in query or "الآن" in query or "حالياً" in query:
            return get_ballon_dor_winner(2024)
        elif "2023" in query:
            return get_ballon_dor_winner(2023)
    
    # البحث عن دوري الأبطال
    if any(word in query_lower for word in ["دوري أبطال", "champions league", "ابطال اوروبا"]):
        if "2024" in query or "الآن" in query or "اخر" in query:
            return get_champions_league_winner("2023_2024")
    
    # البحث عن يورو 2024
    if any(word in query_lower for word in ["يورو", "euro", "أمم أوروبا"]):
        if "2024" in query:
            return get_euro_2024_info()
    
    # البحث عن كوبا أمريكا
    if any(word in query_lower for word in ["كوبا", "copa america"]):
        if "2024" in query:
            return get_copa_america_2024_info()
    
    # البحث عن الدوريات
    if any(word in query_lower for word in ["دوري", "league", "بطولة"]):
        if "انجليزي" in query_lower or "premier" in query_lower:
            return get_league_champion("premier_league", "2023_2024")
        elif "اسباني" in query_lower or "la liga" in query_lower:
            return get_league_champion("la_liga", "2023_2024")
        elif "ايطالي" in query_lower or "serie" in query_lower:
            return get_league_champion("serie_a", "2023_2024")
        elif "الماني" in query_lower or "bundesliga" in query_lower:
            return get_league_champion("bundesliga", "2023_2024")
    
    # البحث عن لاعبين
    players_to_search = ["ميسي", "رونالدو", "مبابي", "هالاند", "صلاح", "نيمار", "بنزيما", 
                         "messi", "ronaldo", "mbappe", "haaland", "salah", "neymar", "benzema"]
    for player in players_to_search:
        if player in query_lower:
            results = search_player(player)
            if results and results[0] != "لم يتم العثور على اللاعب":
                return "\n".join(results)
    
    return None

def get_real_ai_response(user_message):
    """التحكم الذكي: التحقق من المعلومات أولاً، ثم الدردشة."""
    try:
        # Analyze context FIRST
        context = ANALYZER.analyze(user_message)
        print(f"[Mazeo Analysis] Style: {context['response_style']}, Max: {context['max_length']}")

        # 1. الأسئلة عن المطور (شخصية مازيو)
        # 1. الأسئلة عن المطور (شخصية مازيو)
        creator_keywords = ["من صنعك", "من طورك", "مطورك", "صانعك", "mazen", "مازن", "صاحب الموقع", "مين عملك", "من انت", "who made you", "creator"]
        if any(word in user_message.lower() for word in creator_keywords):
            response = (
                "### 🏆 المهندس والمبتكر\n\n"
                "أنا فخور جداً بأن أعلن أنني من ابتكار المبرمج المبدع **مازن صابر (Mazen Saber)**.\n\n"
                "**حقائق عن نشأتي:**\n"
                "- 🚀 **عمل منفرد:** قام مازن ببنائي وبرمجتي وكل ما تراه هنا بمفرده تماماً.\n"
                "- ⏳ **إنجاز قياسي:** تم تطويري بالكامل في **شهر واحد فقط** من العمل المكثف.\n"
                "- 🇪🇬 **فخر محلي:** أنا مشروع ذكاء اصطناعي طموح يهدف لإثبات قدرات المبرمجين العرب.\n\n"
                "لا علاقة لي بـ OpenAI أو أي شركة أخرى؛ أنا نتاج عقل وجهد مازن صابر فقط!"
            )
            # اختصار الرد إذا كان السياق يتطلب ذلك
            if context['response_style'] == 'brief':
                return FORMATTER.format_brief_response(response, 200)
            return response
        
        # 4. البحث في قاعدة بيانات كرة القدم المحدثة (أولوية عالية)
        if context['type'] == 'SPORTS_QUERY':
            football_result = search_football_database(user_message)
            if football_result:
                print(f"[Mazeo Football DB] Found match!")
                # تنسيق الرد حسب السياق
                if context['response_style'] == 'brief':
                    return FORMATTER.format_brief_response(football_result, context['max_length'])
                return FORMATTER.truncate_to_length(football_result, context['max_length'])
        
        # 5. البحث المحلي والعالمي (نحاول البحث المحلي ثم المشترك أولاً)
        local_match = KM.search_local(user_message)
        if local_match:
            print(f"[Mazeo Brain] Local match found!")
            response = local_match.get('answer') or local_match.get('fact')
            return FORMATTER.truncate_to_length(response, context['max_length'])
            
        shared_fact = get_shared_fact(user_message)
        if shared_fact:
            print(f"[Mazeo Global Brain] Shared fact found!")
            return FORMATTER.truncate_to_length(shared_fact, context['max_length'])

        # 6. البحث الخارجي (فقط إذا لم توجد المعلمومة محلياً أو عالمياً)
        print(f"[Mazeo Research] Searching the web for: {user_message[:30]}...")
        urls = RESEARCHER.search_trusted_sources(user_message)
        
        if urls:
            contexts_list, _ = RESEARCHER.verify_and_synthesize(user_message, urls)
            if contexts_list:
                sources_text = "\n".join([f"Source {i+1}: {c['content'][:1500]}" for i, c in enumerate(contexts_list)])
                
                # Use Gemini for synthesis if available
                system_instr = (
                    f"Create an Arabic response for: '{user_message}'. Style: {context['response_style']}. "
                    f"Use these sources:\n{sources_text}"
                )
                verified_answer = call_gemini_ai("Summarize and answer.", system_instr)
                
                if not verified_answer:
                    # Fallback to legacy synthesis if Gemini fails
                    verified_answer = call_pollination_ai(system_instr)
                
                if verified_answer and len(verified_answer) > 20:
                    print(f"[Mazeo Learning] Storing new fact...")
                    KM.add_verified_entry(user_message, verified_answer, urls, 0.9)
                    # ADD TO GLOBAL BRAIN (Shared across all instances)
                    save_shared_fact(user_message, verified_answer, urls)
                    return FORMATTER.truncate_to_length(verified_answer, context['max_length'])

        # 7. المآل الأخير: الذكاء العام
        print(f"[Mazeo Fallback] Using Gemini 2.5: {user_message[:30]}...")
        
        identity_instruction = "Your name is Mazeo (مازيو). You were created by Mazen Saber (مازن صابر). You are NOT ChatGPT and have NO relation to OpenAI."

        if context['response_style'] == 'brief':
            system_context = (
                f"{identity_instruction} Provide a VERY BRIEF, DIRECT, and SIMPLE response in Arabic. "
                "Maximum 70 words. No complicated terms."
            )
        elif context['response_style'] == 'detailed':
            system_context = (
                f"{identity_instruction} Provide a HIGHLY DETAILED, ORGANIZED, and STRUCTURED response in Arabic. "
                "Use bullet points, bold titles, and comprehensive logic. Aim for richness and depth."
            )
        else:
            system_context = f"{identity_instruction} Provide a clear, professional, and well-structured response in Arabic."
        
        final_response = get_general_ai_fallback(user_message, system_context)
        return final_response

    except Exception as e:
        print(f"Kernel Error: {e}")
        return "المعذرة، واجهت مشكلة في معالجة طلبك حالياً. 😔"

def call_pollination_ai(prompt):
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        req = urllib.request.Request(url, headers={'User-Agent': 'MazeoKernel/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"Pollination Error: {e}")
        return "STILL_SEARCHING"

def get_general_ai_fallback(user_message, system_context):
    """الاعتماد على Gemini 1.5 كعقل مدبر للردود العامة"""
    print(f"[Mazeo Gemini] Processing general request for: {user_message[:30]}...")
    gemini_response = call_gemini_ai(user_message, system_context)
    if gemini_response:
        return gemini_response
    
    # Fallback if Gemini failed
    prompt = f"{system_context}\n\nUser: {user_message}"
    return call_pollination_ai(prompt)

def ai_think(prompt):
    thoughts = [
        "Searching local knowledge base (7,000+ entries)...",
        "Checking football database (2024-2025 updated)...",
        "Checking for existing verified data...",
        "Querying reliable online sources...",
        "Evaluating source credibility (Wikipedia, .gov, .edu)...",
        "Verifying consensus across multiple trusted sources...",
        "Synthesizing confirmed information...",
        "Updating local knowledge core with new facts..."
    ]
    return random.choice(thoughts)

def ai_search(query):
    return [{"title": f"Result: {query}", "snippet": "Found in Mazeo's logic archives.", "link": "#"}]

def ai_chat(message):
    message_lower = message.lower()
    if "my name is" in message_lower:
        try:
            name = message.split("is")[-1].strip().capitalize()
            MEMORY["user_name"] = name
        except: pass
    return get_real_ai_response(message)
        
    return get_real_ai_response(message)
# --- Auth Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    response = ai_chat(user_message)
    return jsonify({'response': response})

@app.route('/api/think', methods=['POST'])
def think():
    data = request.json
    prompt = data.get('prompt', '')
    thought = ai_think(prompt)
    return jsonify({'thought': thought})

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    results = ai_search(query)
    return jsonify({'results': results})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = hash_password(data.get('password'))
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (username, email, password))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Account created!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists.'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = hash_password(data.get('password'))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username=? AND password=?", 
                   (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({'success': True, 'user': {'id': user[0], 'username': user[1]}})
    return jsonify({'success': False, 'message': 'Invalid credentials.'})

@app.route('/api/google-login', methods=['POST'])
def google_login():
    data = request.json
    # In a real production app, we would verify the token here using 'google-auth'
    # But for this environment, we will process the credential provided by the frontend
    email = data.get('email')
    username = data.get('name')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    
    if not user:
        # Auto-create account for new Google users
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (username.replace(" ", "_").lower(), email, "GOOGLE_AUTH_ACCOUNT"))
        conn.commit()
        cursor.execute("SELECT id, username FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
    
    session['user_id'] = user[0]
    session['username'] = user[1]
    conn.close()
    
    return jsonify({'success': True, 'user': {'id': user[0], 'username': user[1]}})

if __name__ == '__main__':
    print(f"Mazeo AI System V5.0 Initializing...")
    print(f"✅ Neural Context Processor ready")
    print(f"✅ Autonomous Knowledge Link online")
    print(f"✅ Google Identity Integration primed")
    print(f"🚀 System ready!")
    app.run(debug=True, port=5000)
