import os
import json
import traceback
from dataclasses import dataclass, asdict, field
from medal_processor import award_medals

CURRENT_SESSION_FILE = 'web/activity_history.json'

gamemode = {
    "Osu": "osu",
    "Taiko": "taiko",
    "CatchTheBeat": "fruits",
    "OsuMania": "mania"
}

@dataclass
class GameState:
    # Session states
    session: dict = field(default_factory=lambda: {
        "play_count": {
            "osu": 0,
            "taiko": 0,
            "fruits": 0,
            "mania": 0
        },
        "total_hits": {
            "osu": 0,
            "taiko": 0,
            "fruits": 0,
            "mania": 0
        }
    })
    medals: set = field(default_factory=set)
    
    # Temporary states
    mapsetid: int = 0
    mapid: int = 0
    titleRoman: str = ""
    artistRoman: str = ""
    creator: str = ""
    diffName: str = ""
    drainingtime: int = 0
    breakingtime: int = 0
    rankedStatus: int = 0
    gameMode: str = ""
    modsEnum: int = 0
    starsNomod: float = 0.0
    mStars: float = 0.0
    cs: float = 0.0
    ar: float = 0.0
    od: float = 0.0
    hp: float = 0.0
    mCS: float = 0.0
    mAR: float = 0.0
    mOD: float = 0.0
    mHP: float = 0.0
    circles: int = 0
    sliders: int = 0
    spinners: int = 0
    maxCombo: int = 0
    mainBpm: float = 0.0
    c300: int = 0
    c100: int = 0
    c50: int = 0
    geki: int = 0
    katsu: int = 0
    miss: int = 0
    currentMaxCombo: int = 0
    score: int = 0
    status: int = 0
    grade: int = 0
    acc: float = 0.0
    prev_status: int = 0
    elapsed_time: float = 0.0
    current_time: str = ""
    id: int = 0

    def __post_init__(self):
        with open(CURRENT_SESSION_FILE, 'w') as f:
            f.write("[]")

    def update(self, current_time, elapsed_time, **kwargs):
        setattr(self, "elapsed_time", elapsed_time)
        setattr(self, "current_time", current_time)
        status_update = False

        # Score decreased from above 10k to 0
        if 'score' in kwargs:
            if self.prev_status == 2 and self.score >= 10_000 and kwargs['score'] == 0:
                setattr(self, "grade", 9)
                self.submit_score(passed=False)

        for key, value in kwargs.items():
            if key == "mapBreaks":
                setattr(self, "breakingtime", sum([break_["endTime"] - break_["startTime"] for break_ in value]))
                continue
            if key == "status":
                setattr(self, "prev_status", self.status)
                status_update = True
            
            if key == "gameMode":
                setattr(self, "gameMode", gamemode[value])
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"{key} is not a valid attribute of GameState")
        
            if key == "acc":
                self.acc /= 100

        # 2 (playing) to 32 (score screen)
        if self.prev_status == 2 and self.status == 32 and status_update:
            self.submit_score(passed=True)

    def submit_score(self, passed: bool):
        self.id += 1
        print(f"Score {self.id} submitted")

        self.session["play_count"][self.gameMode] += 1
        self.session["total_hits"][self.gameMode] += self.c300 + self.c100
        if self.gameMode == "osu":
            self.session["total_hits"]["osu"] += self.c50
        elif self.gameMode == "mania":
            self.session["total_hits"]["mania"] += self.c50 + self.geki + self.katsu

        snapshot = asdict(self)
        snapshot["type"] = "score"
        snapshot["pass"] = passed

        # Exclude unnecessary fields in history
        del snapshot["prev_status"]
        del snapshot["medals"]
        del snapshot["session"]

        with open(CURRENT_SESSION_FILE, 'r') as f:
            activity_history = json.load(f)
        activity_history.append(snapshot)
        play_history = [entry for entry in activity_history if entry["type"] == "score"]

        if passed:
            try:
                to_award = award_medals(play_history.copy(), self.session, self.medals)
            except Exception as e:
                print(e)
                traceback.print_exc()
            for medal in to_award:
                self.id += 1
                self.medals.add(medal[0])
                medal_info = {
                    "type": "medal",
                    "medal_id": medal[0],
                    "name": medal[1],
                    "description": medal[2],
                    "elapsed_time": play_history[-1]["elapsed_time"],
                    "current_time": play_history[-1]["current_time"],
                    "id": self.id,
                    "count": len(self.medals)
                }
                activity_history.append(medal_info)

        with open(CURRENT_SESSION_FILE, 'w') as f:
            json.dump(activity_history, f, indent=2)

        print(f"Play history updated at {CURRENT_SESSION_FILE}")
