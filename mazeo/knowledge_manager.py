import json
import os
import datetime
from difflib import SequenceMatcher

class KnowledgeManager:
    def __init__(self, file_path='massive_facts.json'):
        self.file_path = os.path.abspath(file_path)
        self.sector_data = [] # Data from .py files (static)
        self.external_data = [] # Data from .json file (growing)
        self.load_initial_knowledge()
        self.load_data()

    def load_initial_knowledge(self):
        try:
            from knowledge import KNOWLEDGE_BASE
            count = 0
            for category, records in KNOWLEDGE_BASE.items():
                if isinstance(records, list):
                    for r in records:
                        self.sector_data.append({
                            "fact": r if isinstance(r, str) else str(r),
                            "category": category,
                            "source": "Initial Mazeo Brain"
                        })
                        count += 1
            print(f"[KnowledgeManager] Loaded {count} initial sector facts.")
        except Exception as e:
            print(f"Error loading initial knowledge: {e}")

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.external_data = data
                    print(f"[KnowledgeManager] Loaded {len(self.external_data)} facts from {self.file_path}.")
            except Exception as e:
                print(f"Error loading knowledge base: {e}")
        else:
            print(f"[KnowledgeManager] No external database found at {self.file_path}. Creating new.")

    def save_data(self):
        try:
            # We ONLY save external_data to avoid duplicating sector data
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.external_data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno()) # Force write to disk
            print(f"[KnowledgeManager] Successfully saved {len(self.external_data)} entries to {self.file_path}.")
        except Exception as e:
            print(f"Error saving knowledge base: {e}")

    def similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def search_local(self, query, threshold=0.6):
        import re
        def clean(text):
            return re.sub(r'[^\w\s]', '', text.lower()).split()

        query_words = set(clean(query))
        if not query_words:
            return None

        best_match = None
        highest_score = 0

        # Combine both datasets for searching
        all_data = self.sector_data + self.external_data

        for entry in all_data:
            text_to_check = entry.get('fact', '') or entry.get('question', '')
            if not text_to_check:
                continue
            
            text_words = clean(text_to_check)
            text_words_set = set(text_words)
            
            # Keyword overlap
            overlap = len(query_words.intersection(text_words_set)) / len(query_words)
            
            # Sequence matching
            seq_score = self.similarity(query, text_to_check)
            
            combined_score = (overlap * 0.7) + (seq_score * 0.3)
            
            if combined_score > highest_score:
                highest_score = combined_score
                best_match = entry

        if highest_score > threshold:
            print(f"[KnowledgeManager] Found match with score {highest_score:.2f}")
            return best_match
        return None

    def add_verified_entry(self, question, answer, sources, confidence):
        new_entry = {
            "id": len(self.external_data) + 1,
            "question": question,
            "answer": answer,
            "sources": sources,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_score": confidence,
            "verified": True
        }
        self.external_data.append(new_entry)
        self.save_data()
        return new_entry
