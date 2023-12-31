from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Medal(BaseModel):
    id: int
    name: str
    link: str
    description: str
    restriction: str
    grouping: str
    instructions: Optional[str] = None
    time_awarded: Optional[datetime] = None

    def __str__(self):
        return f"{self.name} ({self.id}) - Awarded at {self.time_awarded}"


class ScoreSettings(BaseModel):
    mode: int
    mods_int: int


class Grade(Enum):
    XH = 0
    SH = 1
    X = 2
    S = 3
    A = 4
    B = 5
    C = 6
    D = 7
    F = 8

    def __lt__(self, other):
        if isinstance(other, int):
            return self.value < other
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return NotImplemented


class ScoreStatistics(BaseModel):
    score: int
    max_combo: int
    count_300: int
    count_100: int
    count_50: int
    count_geki: int
    count_katu: int
    count_miss: int
    grade: Grade
    # Rounded to two decimal places
    accuracy: float
    full_combo: bool


class RankStatus(Enum):
    UNSUBMITTED = 1
    # Unranked = Graveyard / Pending / WIP
    UNRANKED = 2
    RANKED = 4
    APPROVED = 5
    QUALIFIED = 6
    LOVED = 7

    def __lt__(self, other):
        if isinstance(other, int):
            return self.value < other
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return NotImplemented


class Beatmap(BaseModel):
    id: int
    beatmapset_id: int
    status: RankStatus
    map_name: str
    diff_name: str
    artist: str
    creator: str
    # calculated, not from api (slightly inaccurate)
    hit_length: int
    bpm: float
    circles: int
    sliders: int
    spinners: int
    max_combo: int
    cs: float
    ar: float
    od: float
    hp: float
    mcs: float
    mar: float
    mod: float
    mhp: float
    stars: float
    mstars: float


class Score(BaseModel):
    settings: ScoreSettings
    statistics: ScoreStatistics
    beatmap: Beatmap
    passed: bool
    submit_time: datetime

    def __str__(self):
        return f"{self.beatmap.map_name} [{self.beatmap.diff_name}] ({self.beatmap.mstars}*)\n" \
               f"{self.statistics.score} ({self.statistics.accuracy:.2f}%) {self.submit_time.strftime('%Y-%m-%d %H:%M:%S')}\n" \
               f"{self.statistics.grade.name} {self.statistics.max_combo}/{self.beatmap.max_combo}x {self.statistics.count_300}/{self.statistics.count_100}/{self.statistics.count_50}/{self.statistics.count_miss}"


class Session(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    start_time: datetime = Field(default=None)
    playcount_osu: int = Field(default=0)
    playcount_taiko: int = Field(default=0)
    playcount_fruits: int = Field(default=0)
    playcount_mania: int = Field(default=0)
    hitcount_osu: int = Field(default=0)
    hitcount_taiko: int = Field(default=0)
    hitcount_fruits: int = Field(default=0)
    hitcount_mania: int = Field(default=0)
    medals: dict[int, int] = Field(default={})
    play_history: list[Score] = Field(default=[])

    def __str__(self):
        return f"{self.username} ({self.user_id})\n" \
               f"Session started at {self.start_time}\n" \
               f"Plays: {self.playcount_osu}/{self.playcount_taiko}/{self.playcount_fruits}/{self.playcount_mania} \n" \
               f"Hits: {self.hitcount_osu}/{self.hitcount_taiko}/{self.hitcount_fruits}/{self.hitcount_mania} \n" \
               f"Medals: {self.medals}"

    def add_medal(self, medal_id: int, time_achieved: datetime):
        self.medals[medal_id] = time_achieved

    def update(self, play_history: list[Score]):
        self.play_history = play_history
        score = play_history[-1]
        if score.settings.mode == 0:
            self.playcount_osu += 1
            self.hitcount_osu += score.statistics.count_300 + score.statistics.count_100 + score.statistics.count_50
        elif score.settings.mode == 1:
            self.playcount_taiko += 1
            self.hitcount_taiko += score.statistics.count_300 + score.statistics.count_100 + score.statistics.count_50
        elif score.settings.mode == 2:
            self.playcount_fruits += 1
            self.hitcount_fruits += score.statistics.count_300 + score.statistics.count_100 + score.statistics.count_50
        elif score.settings.mode == 3:
            self.playcount_mania += 1
            self.hitcount_mania += score.statistics.count_300 + score.statistics.count_100 + score.statistics.count_50
        with open("log.txt", 'w') as file:
            file.write(str(self) + f"\nScores: {self.play_history}")
        