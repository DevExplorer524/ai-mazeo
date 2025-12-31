
from geography_data import GEOGRAPHY_RECORDS
from history_data import HISTORY_RECORDS
from math_data import MATH_RECORDS
from science_data import SCIENCE_RECORDS
from arabic_heritage_data import HERITAGE_RECORDS
from technology_data import TECH_RECORDS
from sports_data import SPORTS_RECORDS

# Final Mazeo Super-Database (7000+ Items Total)
KNOWLEDGE_BASE = {
    "geography": GEOGRAPHY_RECORDS,
    "history": HISTORY_RECORDS,
    "math": MATH_RECORDS,
    "science": SCIENCE_RECORDS,
    "arabic_heritage": HERITAGE_RECORDS,
    "technology": TECH_RECORDS,
    "sports": SPORTS_RECORDS,
    "summary": "Mazeo is powered by a multi-sector brain containing over 7,000 professional data points.",
    "creator": "Mazen Saber",
    "version": "4.5.0 (Sports & Tech Enhanced)"
}

def get_stats():
    stats = {}
    total = 0
    for key, value in KNOWLEDGE_BASE.items():
        if isinstance(value, list):
            stats[key] = len(value)
            total += len(value)
    stats["total"] = total
    return stats

if __name__ == "__main__":
    print("Database Integrity Check:")
    print(get_stats())
