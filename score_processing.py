import json, time, threading, sys
from medal_processor import award_medals
from models import *
from PySide6.QtWidgets import QApplication
from utils import fetch_live_data
from gui import Stopwatch


# Gamemode identifiers
modes = {
    "Osu": 0,
    "Taiko": 1,
    "CatchTheBeat": 2,
    "OsuMania": 3
}


def get_acc(data):
    match modes[data["gameMode"]]:
        case 2:
            total_hits = data["c300"] + data["c100"] + data["c50"] + data["miss"] + data["katsu"]
        case 3:
            total_hits = data["c300"] + data["c100"] + data["c50"] + data["miss"] + data["geki"] + data["katsu"]
        case _:
            total_hits = data["c300"] + data["c100"] + data["c50"] + data["miss"]

    if total_hits <= 0:
        return 100.00

    match modes[data["gameMode"]]:
        case 1:
            accuracy = round((300 * data["c300"] + 150 * data["c100"])/(300 * total_hits) * 100, 2)
        case 2:
            accuracy = round((data["c300"] + data["c100"] + data["c50"])/(total_hits) * 100, 2)
        case 3:
            accuracy = round((300 * data["c300"] + 300 * data["geki"] + 200 * data["katsu"] + 100 * data["c100"] + 50 * data["c50"])/(300 * total_hits) * 100, 2)
        case _:
            accuracy = round((300 * data["c300"] + 100 * data["c100"] + 50 * data["c50"])/(300 * total_hits) * 100, 2)
    
    return accuracy


def add_play(play_history, data, passed, medal_stopwatch):
    global modes
    settings = ScoreSettings(mode=modes[data["gameMode"]], mods_int=data["modsEnum"])

    accuracy = get_acc(data)
    statistics = ScoreStatistics(score=data["score"], max_combo=data["currentMaxCombo"], count_300=data["c300"], 
                                 count_100=data["c100"], count_50=data["c50"], count_geki=data["geki"], 
                                 count_katu=data["katsu"], count_miss=data["miss"], grade=Grade(data["grade"]), 
                                 accuracy=accuracy, full_combo=(data["currentMaxCombo"]==data["maxCombo"]))
    
    hit_length = data["totaltime"]
    for break_time in data["mapBreaks"]:
        hit_length -= (break_time["endTime"] - break_time["startTime"])
    hit_length = int(round(hit_length/1000))
    beatmap = Beatmap(id=data["mapid"], beatmapset_id=data["mapsetid"], status=RankStatus(data["rankedStatus"]), map_name=data["titleRoman"], 
                      diff_name=data["diffName"], artist=data["artistRoman"], creator=data["creator"], hit_length=hit_length, 
                      bpm=data["mainBpm"], circles=data["circles"], sliders=data["sliders"], spinners=data["spinners"], 
                      max_combo=data["maxCombo"], cs=data["cs"], ar=data["ar"], od=data["od"], hp=data["hp"], mcs=data["mCS"], 
                      mar=data["mAR"], mod=data["mOD"], mhp=data["mHP"], stars=data["starsNomod"], mstars=data["mStars"])
    
    score = Score(settings=settings, statistics=statistics, beatmap=beatmap, passed=passed, submit_time=datetime.now())
    play_history.append(score)
    medal_stopwatch.add_play(score)
    return play_history


def main(medal_stopwatch: Stopwatch):
    # Wait for osu! and StreamCompanion to start
    data = -1
    while data == -1:
        data = fetch_live_data()
        time.sleep(1/30)
    
    play_history = []
    session = Session(user_id=data["banchoId"], username=data["banchoUsername"])
    print(session)

    prev_combo_left = 10**9
    prev_data = fetch_live_data()
    status_score = (data["status"], data["score"])
    while True:
        data = fetch_live_data()
        if data == -1:
            print("timeout")
            continue
        if not session.user_id:
            session.user_id = data["banchoId"]
            session.username = data["banchoUsername"]
        session.start_time = medal_stopwatch.start_time
        tl_h, tl_m, tl_s = map(float, data["timeLeft"].split(":"))
        time_remaining = tl_h*3600 + tl_m*60 + tl_s
        if time_remaining == 0 and data["status"] == 2 and status_score != (data["status"], data["score"]) and data["score"] > 0 and data["comboLeft"] == 0:
            passed = True
            if modes[data["gameMode"]] == 1 and data["playerHp"] < 100: passed = False
            play_history = add_play(play_history, data, passed, medal_stopwatch)
            if passed:
                award_medals(session, play_history, medal_stopwatch)
            session.update(play_history)
            status_score = (data["status"], data["score"])
            print(play_history[-1])
        # failed plays with more than 10,000 score submit
        elif (data["comboLeft"] > prev_combo_left or (data["comboLeft"] == 0 and prev_combo_left > 0 and data["status"] == 1)) \
              and status_score != (data["status"], prev_data["score"]) and prev_data["score"] >= 10_000 and prev_data["status"] == 2 and data["status"] not in [8, 32]:
            passed = False
            play_history = add_play(play_history, prev_data, passed, medal_stopwatch)
            session.update(play_history)
            status_score = (data["status"], prev_data["score"])
            prev_data = data.copy()
            print(play_history[-1])

        # if data["comboLeft"] > prev_combo_left:
        #     print(data["comboLeft"], prev_combo_left, status_score, (data["status"], prev_data["score"]), prev_data["score"])    

        prev_combo_left = data["comboLeft"]
        if data["score"] != 0:
            prev_data = data.copy()
        time.sleep(1/30)


if __name__ == "__main__":
    sys.stderr = open('error_log.txt', 'w')
    app = QApplication(sys.argv)
    medal_stopwatch = Stopwatch()

    main_thread = threading.Thread(target=main, args=(medal_stopwatch,))
    main_thread.daemon = True
    main_thread.start()

    medal_stopwatch.show()
    sys.exit(app.exec())