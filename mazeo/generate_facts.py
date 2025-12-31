
import json
import random

def generate_massive_facts(facts_per_category=1000):
    categories = ["History", "Science", "Tech", "Math", "Geography", "Heritage"]
    
    # Detailed data pools for randomization
    pools = {
        "History": ["Roman Empire", "Ancient Egypt", "Ottoman Empire", "Industrial Revolution", "Renaissance", "World Wars", "Cold War"],
        "Science": ["Physics", "Chemistry", "Biology", "Astronomy", "Geology", "Quantum Mechanics", "Genetics"],
        "Tech": ["Artificial Intelligence", "Blockchain", "Cloud Computing", "Web Development", "Programming Languages", "Cybersecurity"],
        "Math": ["Algebra", "Calculus", "Geometry", "Linear Algebra", "Number Theory", "Statistics"],
        "Geography": ["Continents", "Oceans", "Mountain Ranges", "Capitals", "Eco Systems", "Deserts"],
        "Heritage": ["Arabic Poets", "Islamic Scholars", "Ancient Civilizations", "Arabic Proverbs", "Cultural Landmarks"]
    }
    
    facts = []
    print(f"Generating {facts_per_category * len(categories)} facts...")
    
    fact_id = 1
    for cat in categories:
        print(f"Populating category: {cat}")
        for i in range(1, facts_per_category + 1):
            sub = random.choice(pools[cat])
            fact_text = f"Fact #{fact_id} in {sub}: This is a high-level scientific/historical record in Mazeo's brain regarding {sub}. It contains unique training data for {cat} optimization."
            
            facts.append({
                "id": fact_id,
                "category": cat,
                "subject": sub,
                "fact": fact_text,
                "complexity": random.randint(1, 10)
            })
            fact_id += 1
    
    with open("massive_facts.json", "w", encoding='utf-8') as f:
        json.dump(facts, f, indent=2, ensure_ascii=False)
    
    print(f"Success! Created massive_facts.json with {len(facts)} items.")

if __name__ == "__main__":
    generate_massive_facts(1000) # 1000 per category = 6000 total facts
