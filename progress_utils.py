import csv
from datetime import datetime

def save_progress(wpm, accuracy, status):
    with open("progress.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  
            wpm,                                          
            accuracy,                                     
            status                                        
        ])

def load_completed_race_results(filename="progress.csv", count=10):
    results = []

    try:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 4 and row[3] == "COMPLETED":
                    results.append(row)
    except FileNotFoundError:
        return []

    return results[-count:]



def compute_user_progress_stats(filename="progress.csv"):
    completed = load_completed_race_results(filename)
    races_completed = len(completed)

    if not completed:
        return {
            "avg_speed_last_10_races": 0,
            "avg_speed_all_time": 0,
            "last_race_speed": 0,
            "best_race_speed": 0,
            "races_completed": 0
        }

    all_speeds = [int(row[1]) for row in completed]
    last_10_speeds = all_speeds[-10:]

    avg_speed_last_10 = sum(last_10_speeds) / len(last_10_speeds)
    avg_speed_all_time = sum(all_speeds) / len(all_speeds)
    last_race_speed = all_speeds[-1]
    best_race_speed = max(all_speeds)

    return {
        "avg_speed_last_10_races": round(avg_speed_last_10),
        "avg_speed_all_time": round(avg_speed_all_time),
        "last_race_speed": last_race_speed,
        "best_race_speed": best_race_speed,
        "races_completed": races_completed
    }




