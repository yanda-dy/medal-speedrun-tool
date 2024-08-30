from collections import defaultdict
from medal import Medal, medals, packs, aeon_maps

user_stat_medals = set([13, 20, 21, 22, 23, 24, 28, 31, 32, 33, 45, 46, 47, 48, 50, 51, 52, 53, 291, 292, 293])
pass_fc_medals = set([63, 64, 65, 66, 67, 68, 69, 70, 243, 245, 55, 56, 57, 58, 59, 60, 61, 62, 242, 244, 95, 96, 97, 98, 99, 100, 101, 102, 71, 72, 73, 74, 75, 76, 77, 78, 103, 104, 105, 106, 107, 108, 109, 110, 79, 80, 81, 82, 83, 84, 85, 86, 111, 112, 113, 114, 115, 116, 117, 118, 87, 88, 89, 90, 91, 92, 93, 94])
single_check_medals = set([1, 3, 4, 5, 6, 17, 38, 39, 40, 41, 44, 54, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 168, 170, 171, 172, 173, 174, 175, 176, 177, 178, 192, 193, 194, 195, 196, 197, 199, 200, 201, 202, 204, 216, 217, 218, 219, 220, 221, 222, 223, 225, 273, 276, 277, 278, 279, 280, 281, 285, 286, 287, 298, 299, 301, 305, 318, 319, 321, 322, 324, 327, 328, 333])
multi_check_medals = set([15, 16, 42, 43, 224, 268, 269, 270, 271, 272, 274, 275, 297, 300, 302, 303, 304, 306, 307, 317, 320, 323, 326, 329, 331, 332, 334])
medal_ids = sorted(list(medals.keys()))
rank_map = { 0: "XH", 1: "SH", 2: "X", 3: "S", 4: "A", 5: "B", 6: "C", 7: "D", 9: "F" }

def award_pack_medal(medal_id, play_history, challenge: bool):
    scoreset = set()
    for play in play_history:
        # Exclude difficulty reduction mod for Challenge Packs
        if play["pass"] and (not challenge or play["modsEnum"] & 4355 != 0):
            scoreset.add(play["mapsetid"])
    pack_options = packs[medal_id]
    for pack in pack_options:
        count = 0
        check = False
        for beatmapset in pack["beatmaps"]:
            if beatmapset["Id"] in scoreset:
                count += 1
            if beatmapset["Id"] == play_history[-1]["mapsetid"]:
                check = True
        if check and count == len(pack["beatmaps"]):
            return True
    return False

def award_stat_medal(medal_id, user_stats):
    # Catch 20,000 fruits
    if medal_id == 13:
        return user_stats["total_hits"]["fruits"] >= 20_000
    # 5,000 Plays
    elif medal_id == 20:
        return user_stats["play_count"]["osu"] >= 5_000
    # 15,000 Plays
    elif medal_id == 21:
        return user_stats["play_count"]["osu"] >= 15_000
    # 25,000 Plays
    elif medal_id == 22:
        return user_stats["play_count"]["osu"] >= 25_000
    # Catch 200,000 fruits
    elif medal_id == 23:
        return user_stats["total_hits"]["fruits"] >= 200_000
    # Catch 2,000,000 fruits
    elif medal_id == 24:
        return user_stats["total_hits"]["fruits"] >= 2_000_000
    # 50,000 Plays
    elif medal_id == 28:
        return user_stats["play_count"]["osu"] >= 50_000
    # 30,000 Drum Hits
    elif medal_id == 31:
        return user_stats["total_hits"]["taiko"] >= 30_000
    # 300,000 Drum Hits
    elif medal_id == 32:
        return user_stats["total_hits"]["taiko"] >= 300_000
    # 3,000,000 Drum Hits
    elif medal_id == 33:
        return user_stats["total_hits"]["taiko"] >= 3_000_000
    # Jack of All Trades
    elif medal_id == 45:
        osu_playcount = user_stats["play_count"]["osu"]
        taiko_playcount = user_stats["play_count"]["taiko"]
        fruits_playcount = user_stats["play_count"]["fruits"]
        mania_playcount = user_stats["play_count"]["mania"]
        return (osu_playcount >= 5_000) and (taiko_playcount >= 5_000) and (fruits_playcount >= 5_000) and (mania_playcount >= 5_000)
    # 40,000 Keys
    elif medal_id == 46:
        return user_stats["total_hits"]["mania"] >= 40_000
    # 400,000 Keys
    elif medal_id == 47:
        return user_stats["total_hits"]["mania"] >= 400_000
    # 4,000,000 Keys
    elif medal_id == 48:
        return user_stats["total_hits"]["mania"] >= 4_000_000
    
    # Rank-based medals are not activated
    # I Can See The Top
    elif medal_id == 50:
        return False
    # The Gradual Rise
    elif medal_id == 51:
        return False
    # Scaling Up
    elif medal_id == 52:
        return False
    # Approaching The Summit
    elif medal_id == 53:
        return False

    # 30,000,000 Drum Hits
    elif medal_id == 291:
        return user_stats["total_hits"]["taiko"] >= 30_000_000
    # Catch 20,000,000 fruits
    elif medal_id == 292:
        return user_stats["total_hits"]["fruits"] >= 20_000_000
    # 40,000,000 Keys
    elif medal_id == 293:
        return user_stats["total_hits"]["mania"] >= 40_000_000
    else:
        return False

def award_skill_medal(medal_id, score):
    perfect = (score["currentMaxCombo"] == score["maxCombo"])
    if score["gameMode"] == "mania":
        perfect = (score["c50"] + score["miss"] == 0)
    star_rating = score["mStars"]
    # Rising Star, Constellation Prize, Building Confidence, Insanity Approaches, These Clarion Skies, Above and Beyond, Supremacy, Absolution
    if 55 <= medal_id <= 62:
        return medal_id - 54 <= star_rating < medal_id - 53
    # Totality, Business As Usual, Building Steam, Moving Forward, Paradigm Shift, Anguish Quelled, Never Give Up, Aberration
    elif 63 <= medal_id <= 70:
        return perfect and (medal_id - 62 <= star_rating < medal_id - 61)
    # My First Don, Katsu Katsu Katsu, Not Even Trying, Face Your Demons, The Demon Within, Drumbreaker, The Godfather, Rhythm Incarnate
    elif 71 <= medal_id <= 78:
        return medal_id - 70 <= star_rating < medal_id - 69
    # A Slice Of Life, Dashing Ever Forward, Zesty Disposition, Hyperdash ON!, It's Raining Fruit, Fruit Ninja, Dreamcatcher, Lord of the Catch
    elif 79 <= medal_id <= 86:
        return medal_id - 78 <= star_rating < medal_id - 77
    # First Steps, No Normal Player, Impulse Drive, Hyperspeed, Ever Onwards, Another Surpassed, Extra Credit, Maniac
    elif 87 <= medal_id <= 94:
        return medal_id - 86 <= star_rating < medal_id - 85
    # Keeping Time, To Your Own Beat, Big Drums, Adversity Overcome, Demonslayer, Rhythm's Call, Time Everlasting, The Drummer's Throne
    elif 95 <= medal_id <= 102:
        return perfect and (medal_id - 94 <= star_rating < medal_id - 93)
    # Sweet And Sour, Reaching The Core, Clean Platter, Between The Rain, Addicted, Quickening, Supersonic, Dashing Scarlet
    elif 103 <= medal_id <= 110:
        return perfect and (medal_id - 102 <= star_rating < medal_id - 101)
    # Keystruck, Keying In, Hyperflow, Breakthrough, Everything Extra, Level Breaker, Step Up, Behind The Veil
    elif 111 <= medal_id <= 118:
        return perfect and (medal_id - 110 <= star_rating < medal_id - 109)
    # Event Horizon
    elif medal_id == 242:
        return 9 <= star_rating < 10
    # Chosen
    elif medal_id == 243:
        return perfect and (9 <= star_rating < 10)
    # Phantasm
    elif medal_id == 244:
        return 10 <= star_rating < 11
    # Unfathomable
    elif medal_id == 245:
        return perfect and (10 <= star_rating < 11)
    else:
        return False

def award_basic_medal(medal_id, score):
    score["acc"] /= 100
    drain_time = round((score["drainingtime"] - score["breakingtime"]) / 1000)
    perfect = (score["currentMaxCombo"] == score["maxCombo"])
    if score["gameMode"] == "mania":
        perfect = (score["c100"] + score["c50"] + score["miss"] == 0)
    # 500 Combo
    if medal_id == 1:
        return score["currentMaxCombo"] >= 500
    # 750 Combo
    elif medal_id == 3:
        return score["currentMaxCombo"] >= 750
    # 1,000 Combo
    elif medal_id == 4:
        return score["currentMaxCombo"] >= 1_000
    # 2,000 Combo
    elif medal_id == 5:
        return score["currentMaxCombo"] >= 2_000
    # Don't let the bunny distract you!
    elif medal_id == 6:
        return (score["mapid"] in [8707, 8708]) and perfect
    # Non-stop Dancer
    elif medal_id == 17:
        return (score["mapid"] == 9007) and (score["score"] > 3_000_000) and (score["modsEnum"] & 1 == 0)
    # Consolation Prize
    elif medal_id == 38:
        return (score["modsEnum"] in [0, 4]) and (rank_map[score["grade"]] == "D") and (score["score"] > 100_000)
    # Challenge Accepted
    elif medal_id == 39:
        # return (rank_map[score["grade"]] in ["A", "S", "SH", "X", "XH"]) and (score.beatmap.status.name == "APPROVED")
        return score["rankedStatus"] == 5
    # Stumbler
    elif medal_id == 40:
        return perfect and (score["acc"] < 0.85)
    # Jackpot
    elif medal_id == 41:
        if score["score"] < 100_000:
            return False
        else:
            score_str = str(score["score"])
            return len(set(score_str)) == 1
    # Nonstop
    elif medal_id == 44:
        return perfect and (drain_time > 520)
    # Twin Perspectives
    elif medal_id == 54:
        return score["currentMaxCombo"] >= 100
    # Finality
    elif medal_id == 119:
        return score["modsEnum"] == 32
    # Perfectionist
    elif medal_id == 120:
        return score["modsEnum"] == 16416
    # Rock Around The Clock
    elif medal_id == 121:
        return score["modsEnum"] == 16
    # Time And A Half
    elif medal_id == 122:
        return score["modsEnum"] == 64
    # Sweet Rave Party
    elif medal_id == 123:
        return score["modsEnum"] == 576
    # Blindsight
    elif medal_id == 124:
        return score["modsEnum"] == 8
    # Are You Afraid Of The Dark?
    elif medal_id == 125:
        return score["modsEnum"] == 1024
    # Dial It Right Back
    elif medal_id == 126:
        return score["modsEnum"] == 2
    # Risk Averse
    elif medal_id == 127:
        return score["modsEnum"] == 1
    # Slowboat
    elif medal_id == 128:
        return score["modsEnum"] == 256
    # Burned Out
    elif medal_id == 131:
        return score["modsEnum"] == 4096
    # Perseverance
    elif medal_id == 132:
        return drain_time >= 420
    # Feel The Burn
    elif medal_id == 133:
        return perfect and (drain_time >= 420)
    # Time Dilation
    elif medal_id == 134:
        return (score["modsEnum"] & 64 == 64) and (score["modsEnum"] & 1 == 0) and (drain_time >= 720)
    # Just One Second
    elif medal_id == 135:
        return (score["modsEnum"] & 1032 == 1032) and (score["mAR"] >= 8.5)
    # Afterimage
    elif medal_id == 136:
        return score["modsEnum"] == 264
    # To The Core
    elif medal_id == 137:
        return (score["modsEnum"] & 64 == 64) and (score["modsEnum"] & 4355 == 0) and (("nightcore" in score["titleRoman"].lower()) or ("nightcore" in score["artistRoman"].lower()))
    # Prepared
    elif medal_id == 138:
        return perfect and (score["modsEnum"] & 1 == 1)
    # Eclipse
    elif medal_id == 139:
        return score["modsEnum"] == 1032
    # Reckless Abandon
    elif medal_id == 140:
        return (score["modsEnum"] == 48) and (score["mStars"] >= 3)
    # Tunnel Vision
    elif medal_id == 141:
        if (score["circles"] + 2 * score["sliders"] + 3 * score["spinners"]) < 400:
            return False
        else:
            return (score["modsEnum"] & 1024 == 1024) and (score["currentMaxCombo"] < 200)
    # Behold No Deception
    elif medal_id == 142:
        return (score["modsEnum"] & 2 == 2) and perfect and (score["mStars"] >= 4)
    # Up For The Challenge
    elif medal_id == 143:
        return (score["modsEnum"] & 16 == 16) and (score["ar"] >= 7.2) and (score["od"] >= 7.2) and (score["hp"] >= 7.2)
    # Lights Out
    elif medal_id == 144:
        return score["modsEnum"] == 1600
    # Unstoppable
    elif medal_id == 145:
        return (score["modsEnum"] & 80 == 80) and (score["ar"] >= 7.2) and (score["od"] >= 7.2) and (score["hp"] >= 7.2) and (score["mainBpm"] >= 160)
    # Is This Real Life?
    elif medal_id == 146:
        return perfect and (score["modsEnum"] & 80 == 80) and (score["ar"] >= 7.2) and (score["od"] >= 7.2) and (score["hp"] >= 7.2) and (score["mainBpm"] >= 160)
    # Camera Shy
    elif medal_id == 147:
        return score["modsEnum"] == 9
    # The Sum Of All Fears
    elif medal_id == 148:
        return (score["currentMaxCombo"] + 1 == score["maxCombo"]) and (score["miss"] == 1)
    # Dekasight
    elif medal_id == 149:
        return perfect and (score["modsEnum"] == 1034) and (score["mStars"] >= 3)
    # Hour Before The Dawn
    elif medal_id == 150:
        return perfect and (score["mapsetid"] == 151720)
    # Slow And Steady
    elif medal_id == 151:
        return perfect and (score["modsEnum"] == 16672)
    # No Time To Spare
    elif medal_id == 152:
        return perfect and (score["modsEnum"] & 64 == 64) and (drain_time <= 45)
    # Sognare
    elif medal_id == 153:
        return score["modsEnum"] & 256 == 256
    # Realtor Extraordinaire
    elif medal_id == 154:
        return perfect and (score["mapsetid"] == 360680) and (score["modsEnum"] & 80 == 80)
    # Realität
    elif medal_id == 155:
        return (score["mapid"] == 529285) and (score["acc"] >= 0.90)
    # Our Mechanical Benefactors
    elif medal_id == 156:
        return (score["mapid"] == 260489) and (score["acc"] >= 0.85)
    # Meticulous
    elif medal_id == 157:
        return perfect and (score["modsEnum"] == 16418) and (score["mStars"] >= 3)
    # Infinitesimal
    elif medal_id == 158:
        return perfect and (score["modsEnum"] & 16 == 16) and (score["cs"] >= 6)
    # Equilibrium
    elif medal_id == 159:
        if (score["c300"] < 15) or (score["c100"] < 15) or (score["c50"] < 15):
            return False
        return (score["c300"] == score["c100"]) and (score["c100"] == score["c50"])
    # Impeccable
    elif medal_id == 160:
        return perfect and (score["modsEnum"] in [16480, 16992])
    # Elite
    elif medal_id == 161:
        return (score["currentMaxCombo"] == 1337) and (score["maxCombo"] >= 1500) and (score["ar"] >= 8) and (score["od"] >= 8) and (score["starsNomod"] >= 3.5)
    # 50/50
    elif medal_id == 168:
        return score["c50"] == 50
    # Thrill of the Chase
    elif medal_id == 170:
        return perfect and (score["modsEnum"] & 64 == 64) and (score["mapsetid"] == 488238) and (score["mStars"] >= 2.5)
    # The Girl in the Forest
    elif medal_id == 171:
        return (score["currentMaxCombo"] == 151) and (score["acc"] >= 0.95) and (score["mapsetid"] == 40440)
    # You Can't Hide
    elif medal_id == 172:
        return perfect and (score["modsEnum"] == 1032) and (score["mStars"] >= 4)
    # True Torment
    elif medal_id == 173:
        return (score["mapid"] == 1257904) and (score["acc"] >= 0.70)
    # The Firmament Moves
    elif medal_id == 174:
        count_mods = 0
        for mod in [8, 16, 64, 1024]:
            if score["modsEnum"] & mod == mod:
                count_mods += 1
        return (score["mapsetid"] in [486535, 489524]) and (score["mStars"] >= 3) and (count_mods >= 3)
    # Too Fast, Too Furious
    elif medal_id == 175:
        return (score["mapsetid"] == 486142) and (score["modsEnum"] & 64 == 64)
    # Feelin' It
    elif medal_id == 176:
        rounded_bpm = int(round(score["mainBpm"] + 0.00001)) # round half up
        if score["currentMaxCombo"] == 0:
            return False
        else:
            return (rounded_bpm % score["currentMaxCombo"] == 0) and (rounded_bpm // score["currentMaxCombo"] <= 6)
    # Overconfident
    elif medal_id == 177:
        return (score["modsEnum"] & 1112 != 0) and (score["acc"] < 0.70)
    # Spooked
    elif medal_id == 178:
        return (rank_map[score["grade"]] == "D") & (score["modsEnum"] & 1024 == 1024)
    # Skylord
    elif medal_id == 192:
        return (score["mapid"] == 1656874) and (rank_map[score["grade"]] in ["X", "XH"])
    # B-Rave
    elif medal_id == 193:
        return (score["mapid"] == 1583147) and (score["acc"] >= 0.80)
    # Any%
    elif medal_id == 194:
        return (score["mapsetid"] == 785774) and (score["modsEnum"] & 64 == 64)
    # Mirage
    elif medal_id == 195:
        return (score["mapid"] == 1773372) and perfect
    # Under The Stars
    elif medal_id == 196:
        return (score["mapsetid"] == 795432) and (score["modsEnum"] == 1032) and (score["starsNomod"] >= 4)
    # Senseless
    elif medal_id == 197:
        return (score["mapsetid"] == 789905) and (score["modsEnum"] & 8 == 8) and (score["mStars"] >= 4)
    # Aeon
    elif medal_id == 199:
        return perfect and (score["mapsetid"] in aeon_maps) and (score["modsEnum"] == 1288) and (score["mStars"] >= 4) and (drain_time >= 135)
    # Upon The Wind
    elif medal_id == 200:
        return (score["mapsetid"] == 751771) and (score["modsEnum"] & 8 == 8) and (score["mStars"] >= 4)
    # Vantage
    elif medal_id == 201:
        return score["mapid"] == 1492654
    # Quick Maths
    elif medal_id == 202:
        return (score["mapsetid"] == 751774) and (score["miss"] == 34)
    # Efflorescence
    elif medal_id == 204:
        return score["mapid"] == 994518
    # Inundate
    elif medal_id == 216:
        return (score["mapid"] == 1960198) and (score["modsEnum"] & 64 == 64) and (score["acc"] >= 0.85)
    # Not Bluffing
    elif medal_id == 217:
        return perfect and (score["mapsetid"] == 940377) and (score["modsEnum"] == 1032) and (score["mStars"] >= 4)
    # Eureka!
    elif medal_id == 218:
        return perfect and (score["artistRoman"] == "The Flashbulb") and (score["mStars"] >= 4)
    # Regicide
    elif medal_id == 219:
        return perfect and (score["mapsetid"] == 751785) and (score["mStars"] >= 4)
    # Permadeath
    elif medal_id == 220:
        return (score["mapsetid"] in [966408, 957842, 962141]) and (score["modsEnum"] & 16416 == 32) and (score["mStars"] >= 4)
    # The Future Is Now
    elif medal_id == 221:
        return (score["mapid"] == 1787848) and (score["acc"] >= 0.70)
    # Natural 20
    elif medal_id == 222:
        return perfect and (score["mStars"] >= 5) and (score["c300"] % 20 == 0)
    # Kaleidoscope
    elif medal_id == 223:
        return (score["mapid"] == 2022237) and (score["modsEnum"] == 258) and (score["acc"] >= 0.80)
    # Valediction
    elif medal_id == 225:
        return (score["mapid"] == 2202493) and (score["acc"] >= 0.90)
    # Right On Time
    elif medal_id == 273:
        score_minute = int(score["current_time"].split(":")[1])
        return (score["mapsetid"] == 1089084) and (score_minute == 0)
    # Dead Center
    elif medal_id == 276:
        return perfect and (score["mStars"] >= 3) and (score["circles"] == score["sliders"])
    # In Memoriam
    elif medal_id == 277:
        return perfect and (score["mStars"] >= 4) and (score["modsEnum"] == 1290)
    # Sanguine
    elif medal_id == 278:
        return (score["mapid"] == 131564) and (score["modsEnum"] == 2) and (score["acc"] >= 0.92)
    # Not Again
    elif medal_id == 279:
        return (score["mapsetid"] in [1241523, 1254196]) and (score["miss"] == 1) and (score["acc"] >= 0.99)
    # Final Boss
    elif medal_id == 280:
        return (score["mapid"] == 3333745) and (score["acc"] >= 0.92)
    # Beast Mode
    elif medal_id == 281:
        return (score["mapid"] == 2507884) and (score["acc"] >= 0.98)
    # Deliberation
    elif medal_id == 285:
        return perfect and (score["mStars"] >= 6) and (score["modsEnum"] & 256 == 256)
    # Lightless
    elif medal_id == 286:
        return (score["mapid"] == 278451) and (score["modsEnum"] & 1024 == 1024)
    # When You See It
    elif medal_id == 287:
        return (score["artistRoman"] == "xi") and (round((score["acc"] * 100) % 10, 2) == 7.27)
    # Dark Familiarity
    elif medal_id == 298:
        return perfect and (score["mapid"] == 471598) and (score["modsEnum"] == 40)
    # Unseen Heights
    elif medal_id == 301:
        return score["mStars"] >= 100
    # Astronomic
    elif medal_id == 305:
        return perfect and (score["artistRoman"] == "II-L") and (score["mStars"] >= 6)
    # Clarity
    elif medal_id == 318:
        return score["mapid"] == 1480798
    # Causality
    elif medal_id == 321:
        return (score["mapid"] == 2573493) and (score["acc"] >= 0.75)
    # Abrogation
    elif medal_id == 322:
        return (score["mapid"] == 572525) and (score["acc"] >= 0.72)
    # Anabasis
    elif medal_id == 324:
        return score["mapid"] == 2047089
    # Literal
    elif medal_id == 327:
        return (score["mapsetid"] == 1079811) and (score["miss"] == 1) and (score["c100"] == 0)
    # Divination Break
    elif medal_id == 333:
        return (score["mStars"] >= 5) and (score["artistRoman"] == "Yooh") and (score["titleRoman"] == "Ice Angel") and (score["currentMaxCombo"] + 1 == score["maxCombo"]) and (score["miss"] == 1)

    # User-based medals are not activated
    # Creator's Gambit
    elif medal_id == 299:
        # return score.beatmap.user_id == user.id
        return False
    # Autocreation
    elif medal_id == 319:
        # return score["artistRoman"] == score.beatmapset.creator
        return False
    # Value Your Identity
    elif medal_id == 328:
        # required_combo = 1000 if user.id % 1000 == 0 else user.id % 1000
        # return score["currentMaxCombo"] == required_combo
        return False
    
    else:
        return False

def award_complex_medal(medal_id, play_history, user_stats):
    for i in range(len(play_history)):
        play_history[i]["acc"] /= 100
    play_history.reverse()
    recent_play = play_history[0]
    def drain_time(score):
        return round((score["drainingtime"] - score["breakingtime"]) / 1000)
    def perfect(score):
        return (score["currentMaxCombo"] == score["maxCombo"])
    
    # S-Ranker
    if medal_id == 15:
        maps = set()
        for play in play_history:
            if (play["pass"]) and (rank_map[play["grade"]] in ["S", "SH", "X", "XH"]) and (recent_play["elapsed_time"] - play["elapsed_time"] <= 86400):
                maps.add(play["mapid"])
        return len(maps) >= 5
    # Most Improved
    elif medal_id == 16:
        if rank_map[recent_play["grade"]] not in ["A", "S", "SH", "X", "XH"]:
            return False
        if award_medal:
            for play in play_history:
                award_medal = (play["pass"]) and (play["mapid"] == recent_play["mapid"]) and (rank_map[play["grade"]] == "D") and (play["score"] > 100_000) and (recent_play["elapsed_time"] - play["elapsed_time"] <= 86400)
                if award_medal: return True
        return False
    # Obsessed
    elif medal_id == 43:
        count = 0
        for play in play_history:
            count += (play["mapid"] == recent_play["mapid"])
        return count >= 100
    # AHAHAHAHA
    elif medal_id == 224:
        return award_pack_medal(224, play_history, challenge=True)
    # Ten To One
    elif medal_id == 268:
        if len(play_history) < 2:
            return False
        return (play_history[1]["pass"]) and (drain_time(play_history[1]) >= 600) and (drain_time(recent_play) <= 60)
    # Exquisite
    elif medal_id == 269:
        if len(play_history) < 2:
            return False
        return (play_history[1]["pass"]) and perfect(play_history[1]) and (play_history[1]["modsEnum"] & 32 == 32) and (play_history[1]["mStars"] >= 3) and \
               perfect(recent_play) and (recent_play["modsEnum"] & 32 == 32) and (recent_play["mStars"] >= 3) and (recent_play["mapid"] != play_history[1]["mapid"])
    # Persistence Is Key
    elif medal_id == 270:
        if len(play_history) < 6:
            return False
        for i in range(1, 6):
            if (play_history[i]["pass"]) or (play_history[i]["mapsetid"] != 1048705) or (play_history[i]["mapid"] != recent_play["mapid"]):
                return False
        return True
    # Mad Scientist
    elif medal_id == 271:
        beatmaps = [2396095, 2394569, 2392194, 2387334, 2361608]
        scoreset = set()
        for play in play_history:
            if (play["pass"]) and (play["modsEnum"] & 8 == 8) and (play["modsEnum"] & 4355 == 0) and (play["mapid"] in beatmaps):
                scoreset.add((play["mapid"], play["modsEnum"]))
        return len(scoreset) >= 5
    # Tribulation
    elif medal_id == 272:
        passed_maps = set()
        playcount = defaultdict(int)
        for play in play_history[1:]:
            playcount[play["mapid"]] += 1
            if play["pass"]:
                passed_maps.add(play["mapid"])
        return (playcount[recent_play["mapid"]] >= 100) and (recent_play["mapid"] not in passed_maps)
    # Replica
    elif medal_id == 274:
        replica = {}
        for play in play_history[1:]:
            if play["mapsetid"] in [1132727, 1484383, 1432240]:
                replica[(play["mapsetid"], play["gameMode"], play["acc"])] = play["mapid"]
        key = (recent_play["mapsetid"], recent_play["gameMode"], recent_play["acc"])
        if key in replica:
            return recent_play["mapid"] != replica[key]
        return False
    # All Good
    elif medal_id == 275:
        if len(play_history) < 2:
            return False
        return (recent_play["mapsetid"] == 1050477) and (play_history[1]["mapsetid"] == 1050477) and (recent_play["modsEnum"] == play_history[1]["modsEnum"])
    # Mortal Coils
    elif medal_id == 297:
        return award_pack_medal(297, play_history, challenge=True)
    # Time Sink
    elif medal_id == 300:
        if len(play_history) < 2:
            return False
        return (play_history[1]["mapsetid"] == 9215) and (recent_play["mapsetid"] == 1537993)
    # You're Here Forever
    elif medal_id == 302:
        if len(play_history) < 2:
            return False
        return (recent_play["elapsed_time"] - play_history[1]["elapsed_time"] >= 1209600) and user_stats["play_count"][recent_play["gameMode"]] >= 2500
    # True North
    elif medal_id == 304:
        if len(play_history) < 10:
            return False
        mapsets = set()
        for i in range(10):
            mapsets.add(play_history[i]["mapsetid"])
        if len(mapsets) != 10:
            return False
        for i in range(1, 10):
            if play_history[i]["creator"].lower() != recent_play["creator"].lower():
                return False
        return True
    # Superfan
    elif medal_id == 306:
        if len(play_history) < 10:
            return False
        mapsets = set()
        for i in range(10):
            mapsets.add(play_history[i]["mapsetid"])
        if len(mapsets) != 10:
            return False
        for i in range(1, 10):
            if play_history[i]["artistRoman"].lower() != recent_play["artistRoman"].lower():
                return False
        return True
    # Iron Will
    elif medal_id == 307:
        award_medal = award_pack_medal(307, play_history, challenge=True)
    # Resurgence
    elif medal_id == 317:
        if len(play_history) < 2:
            return False
        return ("ashes" in play_history[1]["titleRoman"].lower()) and (recent_play["titleRoman"] == "Immortal Flame (feat. Anna Yvette)")
    # Star Power
    elif medal_id == 320:
        if len(play_history) < 2:
            return False
        orig_mods = play_history[1]["modsEnum"]
        if (rank_map[play_history[1]["grade"]] in ["X", "XH"]) and (orig_mods & 16 == 0):
            return (rank_map[recent_play["grade"]] in ["X", "XH"]) and (recent_play["modsEnum"] & 16 == 16) and (recent_play["mStars"] >= 4) and (recent_play["modsEnum"] & orig_mods == orig_mods)
        return False
    # Internment
    elif medal_id == 323:
        if len(play_history) < 3:
            return False
        award_medal_1 = (play_history[2]["mapid"] == 3022086) and (play_history[2]["currentMaxCombo"] == 255) and (play_history[1]["mapid"] == 3022086) and (play_history[1]["currentMaxCombo"] == 104) and (recent_play["mapid"] == 3022086) and (recent_play["currentMaxCombo"] == 108)
        award_medal_2 = (play_history[2]["mapid"] == 4052455) and (play_history[2]["currentMaxCombo"] == 243) and (play_history[1]["mapid"] == 4052455) and (play_history[1]["currentMaxCombo"] == 76) and (recent_play["mapid"] == 4052455) and (recent_play["currentMaxCombo"] == 133)
        return (award_medal_1 or award_medal_2)
    # Banana Republic
    elif medal_id == 329:
        if len(play_history) < 2:
            return False
        return (rank_map[play_history[1]["grade"]] in ["X", "XH"]) and (recent_play["score"] > play_history[1]["score"]) and (recent_play["acc"] < play_history[1]["acc"])
    # Dexterity
    elif medal_id == 331:
        for play in play_history:
            if (play["pass"]) and (play["acc"] >= 0.95) and (play["mapsetid"] == recent_play["mapsetid"]) and (play["mapid"] != recent_play["mapid"]) and (play["cs"] != recent_play["cs"]):
                return True
        return False
    # Hybrid Hyperion
    elif medal_id == 332:
        recents = {"osu": None, "taiko": None, "fruits": None, "mania": None}
        for play in play_history:
            if recents[play["gameMode"]] is not None:
                recents[play["gameMode"]] = play
            if all(recents.values()):
                break
        if not all(recents.values()):
            return False
        for mode in recents:
            if (recents[mode]["mStars"] < 4) or (rank_map[recents[mode]["grade"]] not in ["A", "S", "SH", "X", "XH"]) or (recents[mode]["mapsetid"] != recent_play["mapsetid"]):
                return False
        return True
    
    # The following medals are not activated (impractical or can't check without the API)
    # Quick Draw
    if medal_id == 42:
        return False
    # Hospitality
    elif medal_id == 303:
        return False
    # Festive Fever
    elif medal_id == 326:
        # Shouldn't be available until December
        return False
    # Unwilted
    elif medal_id == 334:
        return False
    
    else:
        return False

def award_medals(play_history: list, session_statistics: dict, awarded_medals: set):
    if len(play_history) == 0:
        return []

    recent_play = play_history[-1]
    # Play must be a pass on a ranked / approved / qualified / loved map
    if (not recent_play["pass"]) or (recent_play["rankedStatus"] not in [4, 5, 6, 7]): return []
    # Exclude unranked mods: RX, AT, AP, CM, TP, CP, 1K, 2K, 3K
    if recent_play["modsEnum"] & 515909760 != 0: return []
    # HR is unranked in mania
    if (recent_play["gameMode"] == "mania") and (recent_play["modsEnum"] & 16 != 0): return []

    to_award = []
    for medal_id in medal_ids:
        medal = medals[medal_id]
        # Check if medal has already been awarded
        if medal in awarded_medals: continue
        # Medal must be in the correct gamemode
        if medal.restriction != recent_play["gameMode"] and medal.restriction != "NULL": continue
        if medal.grouping in ["Skill & Dedication", "Hush-Hush (Expert)", "Beatmap Challenge Packs"]:
            # Exclude difficulty reduction mods: EZ, NF, HT, SO
            if recent_play["modsEnum"] & 4355 != 0: continue
        if medal.grouping == "Skill & Dedication":
            # Play must be on a ranked / approved map
            if recent_play["rankedStatus"] not in [4, 5]: continue

        award_medal = False
        if medal.grouping in ["Beatmap Packs", "Beatmap Challenge Packs", "Beatmap Spotlights"]:
            challenge_pack = (medal.grouping == "Beatmap Challenge Packs")
            award_medal = award_pack_medal(medal.id, play_history, challenge_pack)
        elif medal_id in user_stat_medals:
            award_medal = award_stat_medal(medal, session_statistics)
        elif medal_id in pass_fc_medals:
            award_medal = award_skill_medal(medal, recent_play)
        elif medal_id in single_check_medals:
            award_medal = award_basic_medal(medal, recent_play)
        elif medal_id in multi_check_medals:
            award_medal = award_complex_medal(medal, play_history, session_statistics)
        else:
            print(f"Medal with ID {medal_id} not found")

        if award_medal:
            to_award.append((medal_id, medal.name, medal.description))

    return to_award
