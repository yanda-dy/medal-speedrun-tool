import json
from datetime import timedelta
from models import *
from gui import Stopwatch


def check_pack(medalid: int, play_history: list[Score], pack_data: dict, challenge: bool):
    scoreset = set()
    for play in play_history:
        if play.passed and (not challenge or play.settings.mods_int & 4355 != 0):
            scoreset.add(play.beatmap.beatmapset_id)
    for medal in pack_data:
        if int(medal["medalid"]) == medalid:
            packs = medal["packs"]
            break
    for pack in packs:
        count = 0
        check = False
        for beatmap in pack["beatmaps"]:
            if beatmap["Id"] in scoreset:
                count += 1
            if beatmap["Id"] == play_history[-1].beatmap.id:
                check = True
        if check and count == len(pack["beatmaps"]):
            return True
    return False


def award_medals(session: Session, play_history: list[Score], medal_stopwatch: Stopwatch):
    mode_name = {
        0: "osu",
        1: "taiko",
        2: "fruits",
        3: "mania"
    }

    medal_data = json.load(open("medal_data.json", "r"))
    medal_data = [Medal(id=medal["medalid"], name=medal["name"], link=medal["link"], description=medal["description"], restriction=medal["restriction"], grouping=medal["grouping"], instructions=medal["instructions"]) for medal in medal_data]
    pack_data = json.load(open("pack_data.json", "r"))

    recent_play = play_history[-1]
    # Play must be a pass on a ranked / approved / qualified / loved map
    if (not recent_play.passed) or (recent_play.beatmap.status not in [4, 5, 6, 7]): return
    # unranked_mods = ["RX", "AT", "AP", "CM", "TP", "CP", "1K", "2K", "3K"]
    if recent_play.settings.mods_int & 515909760 != 0: return
    # HR is unranked in mania
    if (mode_name[recent_play.settings.mode] == "mania") and (recent_play.settings.mods_int & 16 != 0): return
    
    for medal in medal_data:
        if medal.id in session.medals: continue
        if medal.restriction != mode_name[recent_play.settings.mode] and medal.restriction != "NULL": continue
        
        challenge_pack = medal.grouping == "Beatmap Challenge Packs"
        if medal.grouping in ["Skill & Dedication", "Hush-Hush (Expert)", "Beatmap Challenge Packs"]:
            # diff_reduction = ["EZ", "NF", "HT", "SO"]
            if recent_play.settings.mods_int & 4355 != 0: continue
        if medal.grouping == "Skill & Dedication":
            # Play must be on a ranked / approved map
            if recent_play.beatmap.status not in [4, 5]: continue

        award_medal = False
        if medal.grouping in ["Beatmap Packs", "Beatmap Challenge Packs"]:
            award_medal = check_pack(medal.id, play_history, pack_data, challenge_pack)
        
        match medal.id:
            # 500 Combo
            case 1:
                award_medal = recent_play.statistics.max_combo >= 500
            # 750 Combo
            case 3:
                award_medal = recent_play.statistics.max_combo >= 750
            # 1,000 Combo
            case 4:
                award_medal = recent_play.statistics.max_combo >= 1_000
            # 2,000 Combo
            case 5:
                award_medal = recent_play.statistics.max_combo >= 2_000
            # Don't let the bunny distract you!
            case 6:
                award_medal = (recent_play.beatmap.id in [8707, 8708]) and (recent_play.statistics.full_combo)
            # Video Game Pack vol.1
            case 7:
                pass
            # Rhythm Game Pack vol.1
            case 8:
                pass
            # Internet! Pack vol.1
            case 9:
                pass
            # Anime Pack vol.1
            case 10:
                pass
            # Video Game Pack vol.2
            case 11:
                pass
            # Anime Pack vol.2
            case 12:
                pass
            # Catch 20,000 fruits
            case 13:
                award_medal = session.hitcount_fruits >= 20_000
            # Video Game Pack vol.3
            case 14:
                pass
            # S-Ranker
            case 15:
                maps = set()
                for play in play_history:
                    if (play.passed) and (play.statistics.grade <= 3) and (recent_play.submit_time - play.submit_time <= timedelta(hours=24)):
                        maps.add(play.beatmap.id)
                award_medal = len(maps) >= 5
            # Most Improved
            case 16:
                if recent_play.statistics.grade > 4: continue
                for play in play_history:
                    if (play.passed) and (play.beatmap.id == recent_play.beatmap.id) and (play.statistics.grade == 7) and (play.statistics.score > 100_000) and (recent_play.submit_time - play.submit_time <= timedelta(hours=24)):
                        award_medal = True
                        break
            # Non-stop Dancer
            case 17:
                award_medal = (recent_play.beatmap.id == 9007) and (recent_play.statistics.score > 3_000_000) and (recent_play.settings.mods_int & 1 == 0)
            # Internet! Pack vol.2
            case 18:
                pass
            # Rhythm Game Pack vol.2
            case 19:
                pass
            # 5,000 Plays
            case 20:
                award_medal = session.playcount_osu >= 5_000
            # 15,000 Plays
            case 21:
                award_medal = session.playcount_osu >= 15_000
            # 25,000 Plays
            case 22:
                award_medal = session.playcount_osu >= 25_000
            # Catch 200,000 fruits
            case 23:
                award_medal = session.hitcount_fruits >= 200_000
            # Catch 2,000,000 fruits
            case 24:
                award_medal = session.hitcount_fruits >= 2_000_000
            # Anime Pack vol.3
            case 25:
                pass
            # Rhythm Game Pack vol.3
            case 26:
                pass
            # Internet! Pack vol.3
            case 27:
                pass
            # 50,000 Plays
            case 28:
                award_medal = session.playcount_osu >= 50_000
            # 30,000 Drum Hits
            case 31:
                award_medal = session.hitcount_taiko >= 30_000
            # 300,000 Drum Hits
            case 32:
                award_medal = session.hitcount_taiko >= 300_000
            # 3,000,000 Drum Hits
            case 33:
                award_medal = session.hitcount_taiko >= 3_000_000
            # Anime Pack vol.4
            case 34:
                pass
            # Rhythm Game Pack vol.4
            case 35:
                pass
            # Internet! Pack vol.4
            case 36:
                pass
            # Video Game Pack vol.4
            case 37:
                pass
            # Consolation Prize
            case 38:
                award_medal = (recent_play.settings.mods_int in [0, 4]) and (recent_play.statistics.grade == 7) and (recent_play.statistics.score > 100_000) and (len(session.count_medals[medal.id]) > 0)
            # Challenge Accepted
            case 39:
                award_medal = (recent_play.statistics.grade <= 4) and (recent_play.beatmap.status == 5)
            # Stumbler
            case 40:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.statistics.accuracy < 85)
            # Jackpot
            case 41:
                if recent_play.statistics.score < 100_000: continue
                score_str = str(recent_play.statistics.score)
                award_medal = len(set(score_str)) == 1
            # Quick Draw
            case 42:
                # Not implemented
                pass
            # Obsessed
            case 43:
                count = 0
                for play in play_history:
                    count += (play.beatmap.id == recent_play.beatmap.id)
                award_medal = count >= 100
            # Nonstop
            case 44:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.hit_length > 520)
            # Jack of All Trades
            case 45:
                award_medal = (session.playcount_osu >= 5_000) and (session.playcount_taiko >= 5_000) and (session.playcount_fruits >= 5_000) and (session.playcount_mania >= 5_000)
            # 40,000 Keys
            case 46:
                award_medal = session.hitcount_mania >= 40_000
            # 400,000 Keys
            case 47:
                award_medal = session.hitcount_mania >= 400_000
            # 4,000,000 Keys
            case 48:
                award_medal = session.hitcount_mania >= 4_000_000
            # I Can See The Top
            case 50:
                # Not implemented
                pass
            # The Gradual Rise
            case 51:
                # Not implemented
                pass
            # Scaling Up
            case 52:
                # Not implemented
                pass
            # Approaching The Summit
            case 53:
                # Not implemented
                pass
            # Twin Perspectives
            case 54:
                award_medal = recent_play.statistics.max_combo >= 100
            # Rising Star
            case 55:
                award_medal = 1 <= recent_play.beatmap.mstars < 2
            # Constellation Prize
            case 56:
                award_medal = 2 <= recent_play.beatmap.mstars < 3
            # Building Confidence
            case 57:
                award_medal = 3 <= recent_play.beatmap.mstars < 4
            # Insanity Approaches
            case 58:
                award_medal = 4 <= recent_play.beatmap.mstars < 5
            # These Clarion Skies
            case 59:
                award_medal = 5 <= recent_play.beatmap.mstars < 6
            # Above and Beyond
            case 60:
                award_medal = 6 <= recent_play.beatmap.mstars < 7
            # Supremacy
            case 61:
                award_medal = 7 <= recent_play.beatmap.mstars < 8
            # Absolution
            case 62:
                award_medal = 8 <= recent_play.beatmap.mstars < 9
            # Totality
            case 63:
                award_medal = (recent_play.statistics.full_combo) and (1 <= recent_play.beatmap.mstars < 2)
            # Business As Usual
            case 64:
                award_medal = (recent_play.statistics.full_combo) and (2 <= recent_play.beatmap.mstars < 3)
            # Building Steam
            case 65:
                award_medal = (recent_play.statistics.full_combo) and (3 <= recent_play.beatmap.mstars < 4)
            # Moving Forward
            case 66:
                award_medal = (recent_play.statistics.full_combo) and (4 <= recent_play.beatmap.mstars < 5)
            # Paradigm Shift
            case 67:
                award_medal = (recent_play.statistics.full_combo) and (5 <= recent_play.beatmap.mstars < 6)
            # Anguish Quelled
            case 68:
                award_medal = (recent_play.statistics.full_combo) and (6 <= recent_play.beatmap.mstars < 7)
            # Never Give Up
            case 69:
                award_medal = (recent_play.statistics.full_combo) and (7 <= recent_play.beatmap.mstars < 8)
            # Aberration
            case 70:
                award_medal = (recent_play.statistics.full_combo) and (8 <= recent_play.beatmap.mstars < 9)
            # My First Don
            case 71:
                award_medal = 1 <= recent_play.beatmap.mstars < 2
            # Katsu Katsu Katsu
            case 72:
                award_medal = 2 <= recent_play.beatmap.mstars < 3
            # Not Even Trying
            case 73:
                award_medal = 3 <= recent_play.beatmap.mstars < 4
            # Face Your Demons
            case 74:
                award_medal = 4 <= recent_play.beatmap.mstars < 5
            # The Demon Within
            case 75:
                award_medal = 5 <= recent_play.beatmap.mstars < 6
            # Drumbreaker
            case 76:
                award_medal = 6 <= recent_play.beatmap.mstars < 7
            # The Godfather
            case 77:
                award_medal = 7 <= recent_play.beatmap.mstars < 8
            # Rhythm Incarnate
            case 78:
                award_medal = 8 <= recent_play.beatmap.mstars < 9
            # A Slice Of Life
            case 79:
                award_medal = 1 <= recent_play.beatmap.mstars < 2
            # Dashing Ever Forward
            case 80:
                award_medal = 2 <= recent_play.beatmap.mstars < 3
            # Zesty Disposition
            case 81:
                award_medal = 3 <= recent_play.beatmap.mstars < 4
            # Hyperdash ON!
            case 82:
                award_medal = 4 <= recent_play.beatmap.mstars < 5
            # It's Raining Fruit
            case 83:
                award_medal = 5 <= recent_play.beatmap.mstars < 6
            # Fruit Ninja
            case 84:
                award_medal = 6 <= recent_play.beatmap.mstars < 7
            # Dreamcatcher
            case 85:
                award_medal = 7 <= recent_play.beatmap.mstars < 8
            # Lord of the Catch
            case 86:
                award_medal = 8 <= recent_play.beatmap.mstars < 9
            # First Steps
            case 87:
                award_medal = 1 <= recent_play.beatmap.mstars < 2
            # No Normal Player
            case 88:
                award_medal = 2 <= recent_play.beatmap.mstars < 3
            # Impulse Drive
            case 89:
                award_medal = 3 <= recent_play.beatmap.mstars < 4
            # Hyperspeed
            case 90:
                award_medal = 4 <= recent_play.beatmap.mstars < 5
            # Ever Onwards
            case 91:
                award_medal = 5 <= recent_play.beatmap.mstars < 6
            # Another Surpassed
            case 92:
                award_medal = 6 <= recent_play.beatmap.mstars < 7
            # Extra Credit
            case 93:
                award_medal = 7 <= recent_play.beatmap.mstars < 8
            # Maniac
            case 94:
                award_medal = 8 <= recent_play.beatmap.mstars < 9
            # Keeping Time
            case 95:
                award_medal = (recent_play.statistics.full_combo) and (1 <= recent_play.beatmap.mstars < 2)
            # To Your Own Beat
            case 96:
                award_medal = (recent_play.statistics.full_combo) and (2 <= recent_play.beatmap.mstars < 3)
            # Big Drums
            case 97:
                award_medal = (recent_play.statistics.full_combo) and (3 <= recent_play.beatmap.mstars < 4)
            # Adversity Overcome
            case 98:
                award_medal = (recent_play.statistics.full_combo) and (4 <= recent_play.beatmap.mstars < 5)
            # Demonslayer
            case 99:
                award_medal = (recent_play.statistics.full_combo) and (5 <= recent_play.beatmap.mstars < 6)
            # Rhythm's Call
            case 100:
                award_medal = (recent_play.statistics.full_combo) and (6 <= recent_play.beatmap.mstars < 7)
            # Time Everlasting
            case 101:
                award_medal = (recent_play.statistics.full_combo) and (7 <= recent_play.beatmap.mstars < 8)
            # The Drummer's Throne
            case 102:
                award_medal = (recent_play.statistics.full_combo) and (8 <= recent_play.beatmap.mstars < 9)
            # Sweet And Sour
            case 103:
                award_medal = (recent_play.statistics.full_combo) and (1 <= recent_play.beatmap.mstars < 2)
            # Reaching The Core
            case 104:
                award_medal = (recent_play.statistics.full_combo) and (2 <= recent_play.beatmap.mstars < 3)
            # Clean Platter
            case 105:
                award_medal = (recent_play.statistics.full_combo) and (3 <= recent_play.beatmap.mstars < 4)
            # Between The Rain
            case 106:
                award_medal = (recent_play.statistics.full_combo) and (4 <= recent_play.beatmap.mstars < 5)
            # Addicted
            case 107:
                award_medal = (recent_play.statistics.full_combo) and (5 <= recent_play.beatmap.mstars < 6)
            # Quickening
            case 108:
                award_medal = (recent_play.statistics.full_combo) and (6 <= recent_play.beatmap.mstars < 7)
            # Supersonic
            case 109:
                award_medal = (recent_play.statistics.full_combo) and (7 <= recent_play.beatmap.mstars < 8)
            # Dashing Scarlet
            case 110:
                award_medal = (recent_play.statistics.full_combo) and (8 <= recent_play.beatmap.mstars < 9)
            # Keystruck
            case 111:
                award_medal = (recent_play.statistics.full_combo) and (1 <= recent_play.beatmap.mstars < 2)
            # Keying In
            case 112:
                award_medal = (recent_play.statistics.full_combo) and (2 <= recent_play.beatmap.mstars < 3)
            # Hyperflow
            case 113:
                award_medal = (recent_play.statistics.full_combo) and (3 <= recent_play.beatmap.mstars < 4)
            # Breakthrough
            case 114:
                award_medal = (recent_play.statistics.full_combo) and (4 <= recent_play.beatmap.mstars < 5)
            # Everything Extra
            case 115:
                award_medal = (recent_play.statistics.full_combo) and (5 <= recent_play.beatmap.mstars < 6)
            # Level Breaker
            case 116:
                award_medal = (recent_play.statistics.full_combo) and (6 <= recent_play.beatmap.mstars < 7)
            # Step Up
            case 117:
                award_medal = (recent_play.statistics.full_combo) and (7 <= recent_play.beatmap.mstars < 8)
            # Behind The Veil
            case 118:
                award_medal = (recent_play.statistics.full_combo) and (8 <= recent_play.beatmap.mstars < 9)
            # Finality
            case 119:
                award_medal = recent_play.settings.mods_int == 32
            # Perfectionist
            case 120:
                award_medal = recent_play.settings.mods_int == 16416
            # Rock Around The Clock
            case 121:
                award_medal = recent_play.settings.mods_int == 16
            # Time And A Half
            case 122:
                award_medal = recent_play.settings.mods_int == 64
            # Sweet Rave Party
            case 123:
                award_medal = recent_play.settings.mods_int == 576
            # Blindsight
            case 124:
                award_medal = recent_play.settings.mods_int == 8
            # Are You Afraid Of The Dark?
            case 125:
                award_medal = recent_play.settings.mods_int == 1024
            # Dial It Right Back
            case 126:
                award_medal = recent_play.settings.mods_int == 2
            # Risk Averse
            case 127:
                award_medal = recent_play.settings.mods_int == 1
            # Slowboat
            case 128:
                award_medal = recent_play.settings.mods_int == 256
            # Burned Out
            case 131:
                award_medal = recent_play.settings.mods_int == 4096
            # Perseverance
            case 132:
                award_medal = recent_play.beatmap.hit_length >= 420
            # Feel The Burn
            case 133:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.hit_length >= 420)
            # Time Dilation
            case 134:
                award_medal = (recent_play.settings.mods_int & 64 == 64) and (recent_play.settings.mods_int & 1 == 0) and (recent_play.beatmap.hit_length >= 720)
            # Just One Second
            case 135:
                award_medal = (recent_play.settings.mods_int & 1032 == 1032) and (recent_play.beatmap.mar >= 9)
            # Afterimage
            case 136:
                award_medal = recent_play.settings.mods_int == 264
            # To The Core
            case 137:
                award_medal = (recent_play.settings.mods_int & 64 == 64) and (recent_play.settings.mods_int & 4355 == 0) and (("nightcore" in recent_play.beatmap.map_name.lower()) or ("nightcore" in recent_play.beatmap.artist.lower()))
            # Prepared
            case 138:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int & 1 == 1)
            # Eclipse
            case 139:
                award_medal = recent_play.settings.mods_int == 1032
            # Reckless Abandon
            case 140:
                award_medal = (recent_play.settings.mods_int == 48) and (recent_play.beatmap.mstars >= 3)
            # Tunnel Vision
            case 141:
                if (recent_play.beatmap.circles + 2 * recent_play.beatmap.sliders + 3 * recent_play.beatmap.spinners) < 400: continue
                award_medal = (recent_play.settings.mods_int & 1024 == 1024) and (recent_play.statistics.max_combo < 200)
            # Behold No Deception
            case 142:
                award_medal = (recent_play.settings.mods_int & 2 == 2) and (recent_play.statistics.full_combo) and (recent_play.beatmap.mstars >= 4)
            # Up For The Challenge
            case 143:
                award_medal = (recent_play.settings.mods_int & 16 == 16) and (recent_play.beatmap.ar >= 7.2) and (recent_play.beatmap.od >= 7.2) and (recent_play.beatmap.hp >= 7.2)
            # Lights Out
            case 144:
                award_medal = recent_play.settings.mods_int == 1600
            # Unstoppable
            case 145:
                award_medal = (recent_play.settings.mods_int & 80 == 80) and (recent_play.beatmap.ar >= 7.2) and (recent_play.beatmap.od >= 7.2) and (recent_play.beatmap.hp >= 7.2) and (recent_play.beatmap.bpm >= 160)
            # Is This Real Life?
            case 146:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int & 80 == 80) and (recent_play.beatmap.ar >= 7.2) and (recent_play.beatmap.od >= 7.2) and (recent_play.beatmap.hp >= 7.2) and (recent_play.beatmap.bpm >= 160)
            # Camera Shy
            case 147:
                award_medal = recent_play.settings.mods_int == 9
            # The Sum Of All Fears
            case 148:
                award_medal = (recent_play.statistics.max_combo + 1 == recent_play.beatmap.max_combo) and (recent_play.statistics.count_miss == 1)
            # Dekasight
            case 149:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int == 1034) and (recent_play.beatmap.mstars >= 3)
            # Hour Before The Dawn
            case 150:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.beatmapset_id == 151720)
            # Slow And Steady
            case 151:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int == 16672)
            # No Time To Spare
            case 152:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int & 64 == 64) and (recent_play.beatmap.hit_length <= 45)
            # Sognare
            case 153:
                award_medal = recent_play.settings.mods_int & 256 == 256
            # Realtor Extraordinaire
            case 154:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.beatmapset_id == 360680) and (recent_play.settings.mods_int & 80 == 80)
            # Realität
            case 155:
                award_medal = (recent_play.beatmap.id == 529285) and (recent_play.statistics.accuracy >= 90)
            # Our Mechanical Benefactors
            case 156:
                award_medal = (recent_play.beatmap.id == 260489) and (recent_play.statistics.accuracy >= 85)
            # Meticulous
            case 157:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int == 16418) and (recent_play.beatmap.mstars >= 3)
            # Infinitesimal
            case 158:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int & 16 == 16) and (recent_play.beatmap.mcs >= 7.8)
            # Equilibrium
            case 159:
                if (recent_play.statistics.count_300 < 15) or (recent_play.statistics.count_100 < 15) or (recent_play.statistics.count_50 < 15): continue
                award_medal = (recent_play.statistics.count_300 == recent_play.statistics.count_100) and (recent_play.statistics.count_100 == recent_play.statistics.count_50)
            # Impeccable
            case 160:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int in [16480, 16992])
            # Elite
            case 161:
                award_medal = (recent_play.statistics.max_combo == 1337) and (recent_play.beatmap.max_combo >= 1500) and (recent_play.beatmap.ar >= 8) and (recent_play.beatmap.od >= 8) and (recent_play.beatmap.stars >= 3.5)
            # January/February 2017 Spotlight
            case 162:
                pass
            # March 2017 Spotlight
            case 163:
                pass
            # April 2017 Spotlight
            case 164:
                pass
            # May 2017 Spotlight
            case 165:
                pass
            # June 2017 Spotlight
            case 166:
                pass
            # July 2017 Spotlight
            case 167:
                pass
            # 50/50
            case 168:
                award_medal = recent_play.statistics.count_50 == 50
            # August 2017 Spotlight
            case 169:
                pass
            # Thrill of the Chase
            case 170:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int & 64 == 64) and (recent_play.beatmap.beatmapset_id == 488238) and (recent_play.beatmap.mstars >= 2.5)
            # The Girl in the Forest
            case 171:
                award_medal = (recent_play.statistics.max_combo == 151) and (recent_play.statistics.accuracy >= 95) and (recent_play.beatmap.beatmapset_id == 40440)
            # You Can't Hide
            case 172:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.settings.mods_int == 1032) and (recent_play.beatmap.mstars >= 4)
            # True Torment
            case 173:
                award_medal = (recent_play.beatmap.id == 1257904) and (recent_play.statistics.accuracy >= 70)
            # The Firmament Moves
            case 174:
                count_mods = 0
                for mod in [8, 16, 64, 1024]:
                    if recent_play.settings.mods_int & mod == mod:
                        count_mods += 1
                award_medal = (recent_play.beatmap.beatmapset_id in [486535, 489524]) and (recent_play.beatmap.mstars >= 3) and (count_mods >= 3)
            # Too Fast, Too Furious
            case 175:
                award_medal = (recent_play.beatmap.beatmapset_id == 486142) and (recent_play.settings.mods_int & 64 == 64)
            # Feelin' It
            case 176:
                award_medal = (recent_play.beatmap.max_combo == int(recent_play.beatmap.bpm)) or (recent_play.statistics.max_combo == int(recent_play.beatmap.bpm)//2)
            # Overconfident
            case 177:
                award_medal = (recent_play.settings.mods_int & 1112 != 0) and (recent_play.statistics.accuracy < 70)
            # Spooked
            case 178:
                award_medal = (recent_play.statistics.grade == 7) & (recent_play.settings.mods_int & 1024 == 1024)
            # MOtOLOiD
            case 179:
                pass
            # September 2017 Spotlight
            case 180:
                pass
            # October 2017 Spotlight
            case 181:
                pass
            # November 2017 Spotlight
            case 182:
                pass
            # December 2017 Spotlight
            case 183:
                pass
            # January 2018 Spotlight
            case 184:
                pass
            # Mappers' Guild Pack I
            case 185:
                pass
            # February 2018 Spotlight
            case 186:
                pass
            # March 2018 Spotlight
            case 187:
                pass
            # April 2018 Spotlight
            case 188:
                pass
            # Cranky
            case 189:
                pass
            # Mappers' Guild Pack II
            case 190:
                pass
            # High Tea Music
            case 191:
                pass
            # Skylord
            case 192:
                award_medal = (recent_play.beatmap.id == 1656874) and (recent_play.statistics.grade in [0, 2])
            # B-Rave
            case 193:
                award_medal = (recent_play.beatmap.id == 1583147) and (recent_play.statistics.accuracy >= 80)
            # Any%
            case 194:
                award_medal = (recent_play.beatmap.beatmapset_id == 785774) and (recent_play.settings.mods_int & 64 == 64)
            # Mirage
            case 195:
                award_medal = (recent_play.beatmap.id == 1773372) and (recent_play.statistics.full_combo)
            # Under The Stars
            case 196:
                award_medal = (recent_play.beatmap.beatmapset_id == 795432) and (recent_play.settings.mods_int == 1032) and (recent_play.beatmap.stars >= 4)
            # Senseless
            case 197:
                award_medal = (recent_play.beatmap.beatmapset_id == 789905) and (recent_play.settings.mods_int & 8 == 8) and (recent_play.beatmap.mstars >= 4)
            # Aeon
            # TODO: get list of maps ranked 2011 or earlier
            case 199:
                valid_mapsets = []
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.beatmapset_id in valid_mapsets) and (recent_play.settings.mods_int == 1288) and (recent_play.settings.mstars >= 4) and (recent_play.beatmap.hit_length >= 180)
            # Upon The Wind
            case 200:
                award_medal = (recent_play.beatmap.beatmapset_id == 751771) and (recent_play.settings.mods_int & 8 == 8) and (recent_play.beatmap.mstars >= 4)
            # Vantage
            case 201:
                award_medal = recent_play.beatmap.id == 1492654
            # Quick Maths
            case 202:
                award_medal = (recent_play.beatmap.beatmapset_id == 751774) and (recent_play.statistics.count_miss == 34)
            # Efflorescence
            case 204:
                award_medal = recent_play.beatmap.id == 994518
            # Summer 2018 Beatmap Spotlights
            case 205:
                pass
            # Culprate
            case 206:
                pass
            # Fall 2018 Beatmap Spotlights
            case 207:
                pass
            # HyuN
            case 208:
                pass
            # Winter 2019 Beatmap Spotlights
            case 209:
                pass
            # Spring 2019 Beatmap Spotlights
            case 210:
                pass
            # Imperial Circus Dead Decadence
            case 213:
                pass
            # tieff
            case 214:
                pass
            # Summer 2019 Beatmap Spotlights
            case 215:
                pass
            # Inundate
            case 216:
                award_medal = (recent_play.beatmap.id == 1960198) and (recent_play.settings.mods_int & 64 == 64) and (recent_play.statistcs.accuracy >= 85)
            # Not Bluffing
            case 217:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.beatmapset_id == 940377) and (recent_play.settings.mods_int == 1032) and (recent_play.beatmap.mstars >= 4)
            # Eureka!
            case 218:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.artist == "The Flashbulb") and (recent_play.beatmap.mstars >= 4)
            # Regicide
            case 219:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.beatmapset_id == 751785) and (recent_play.beatmap.mstars >= 4)
            # Permadeath
            case 220:
                award_medal = (recent_play.beatmap.beatmapset_id in [966408, 957842, 962141]) and (recent_play.beatmap.beatmapset_id & 16416 == 32) and (recent_play.beatmap.mstars >= 4)
            # The Future Is Now
            case 221:
                award_medal = (recent_play.beatmap.id == 1787848) and (recent_play.statistics.accuracy >= 70)
            # Natural 20
            case 222:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.mstars >= 5) and (recent_play.statistics.count_300 % 20 == 0)
            # Kaleidoscope
            case 223:
                award_medal = (recent_play.beatmap.id == 2022237) and (recent_play.settings.mods_int == 258) and (recent_play.statistics.accuracy >= 80)
            # AHAHAHAHA
            case 224:
                award_medal = check_pack(224, play_history, pack_data, challenge=True)
            # Valediction
            case 225:
                award_medal = (recent_play.beatmap.id == 2202493) and (recent_play.statistics.accuracy >= 90)
            # Mappers' Guild Pack III
            case 226:
                pass
            # Mappers' Guild Pack IV
            case 227:
                pass
            # Autumn 2019 Beatmap Spotlights
            case 228:
                pass
            # Afterparty
            case 229:
                pass
            # Ben Briggs
            case 230:
                pass
            # Carpool Tunnel
            case 231:
                pass
            # Creo
            case 232:
                pass
            # cYsmix
            case 233:
                pass
            # Fractal Dreamers
            case 234:
                pass
            # LukHash
            case 235:
                pass
            # *namirin
            case 236:
                pass
            # onumi
            case 237:
                pass
            # The Flashbulb
            case 238:
                pass
            # Undead Corporation
            case 239:
                pass
            # Wisp X
            case 240:
                pass
            # Winter 2020 Beatmap Spotlights
            case 241:
                pass
            # Event Horizon
            case 242:
                award_medal = 9 <= recent_play.beatmap.mstars < 10
            # Chosen
            case 243:
                award_medal = (recent_play.statistics.full_combo) and (9 <= recent_play.beatmap.mstars < 10)
            # Phantasm
            case 244:
                award_medal = 10 <= recent_play.beatmap.mstars < 11
            # Unfathomable
            case 245:
                award_medal = (recent_play.statistics.full_combo) and (10 <= recent_play.beatmap.mstars < 11)
            # Camellia I
            case 246:
                pass
            # Camellia II
            case 247:
                pass
            # Celldweller
            case 248:
                pass
            # Cranky II
            case 249:
                pass
            # Cute Anime Girls
            case 250:
                pass
            # ELFENSJoN
            case 251:
                pass
            # Hyper Potions
            case 252:
                pass
            # Kola Kid
            case 253:
                pass
            # LeaF
            case 254:
                pass
            # Panda Eyes
            case 255:
                pass
            # PUP
            case 256:
                pass
            # Ricky Montgomery
            case 257:
                pass
            # Rin
            case 258:
                pass
            # S3RL
            case 259:
                pass
            # Sound Souler
            case 260:
                pass
            # Teminite
            case 261:
                pass
            # VINXIS
            case 262:
                pass
            # Mappers' Guild Pack V
            case 263:
                pass
            # Mappers' Guild Pack VI
            case 264:
                pass
            # Mappers' Guild Pack VII
            case 265:
                pass
            # Mappers' Guild Pack VIII
            case 266:
                pass
            # Mappers' Guild Pack IX
            case 267:
                pass
            # Ten To One
            case 268:
                if len(play_history) < 2: continue
                award_medal = (play_history[-2].passed) and (play_history[-2].beatmap.hit_length >= 600) and (recent_play.beatmap.hit_length <= 60)
            # Exquisite
            case 269:
                if len(play_history) < 2: continue
                award_medal = (play_history[-2].passed) and (play_history[-2].statistics.full_combo) and (play_history[-2].settings.mods_int & 32 == 32) and (play_history[-2].beatmap.mstars >= 3) and (recent_play.statistics.full_combo) and (recent_play.settings.mods_int & 32 == 32) and (recent_play.beatmap.mstars >= 3) and (recent_play.beatmap.id != play_history[-2].beatmap.id)
            # Persistence Is Key
            case 270:
                if len(play_history) < 6: continue
                award_medal = True
                for i in range(2, 7):
                    if (play_history[-i].passed) or (play_history[-i].beatmap.beatmapset_id != 1048705) or (play_history[-i].beatmap.id != play_history[-i+1].beatmap.id):
                        award_medal = False
                        break
            # Mad Scientist
            case 271:
                beatmaps = [2396095, 2394569, 2392194, 2387334, 2361608]
                for play in play_history:
                    if (play.passed) and (play.settings.mods_int & 8 == 8) and (play.settings.mods_int & 1 == 0) and (play.beatmap.id in beatmaps):
                        beatmaps.remove(play.beatmap.id)
                award_medal = len(beatmaps) == 0
            # Tribulation
            case 272:
                playcount = {}
                for play in play_history:
                    if play.beatmap.id in playcount:
                        if playcount[play.beatmap.id] == 0: continue
                        playcount[play.beatmap.id] += 1
                    else:
                        playcount[play.beatmap.id] = 1
                    if play.passed:
                        playcount[play.beatmap.id] = 0
                award_medal = playcount[recent_play.beatmap.id] >= 100
            # Right On Time
            case 273:
                award_medal = (recent_play.beatmap.beatmapset_id == 1089084) and (recent_play.submit_time.minute == 0)
            # Replica
            case 274:
                replica = {}
                for play in play_history[:-1]:
                    if play.beatmap.beatmapset_id in [1132727, 1484383, 1432240]:
                        replica[(play.beatmap.beatmapset_id, play.settings.mode, round(play.statistics.accuracy, 2))] = play.beatmap.id
                if (recent_play.beatmap.beatmapset_id, recent_play.settings.mode, round(recent_play.statistics.accuracy, 2)) in replica:
                    award_medal = recent_play.beatmap.id != replica[(recent_play.beatmap.beatmapset_id, recent_play.settings.mode, round(recent_play.statistics.accuracy, 2))]
            # All Good
            case 275:
                if len(play_history) < 2: continue
                award_medal = (recent_play.beatmap.beatmapset_id == 1050477) and (play_history[-2].beatmap.beatmapset_id == 1050477) and (recent_play.settings.mods_int == play_history[-2].settings.mods_int)
            # Dead Center
            case 276:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.mstars >= 3) and (recent_play.beatmap.circles == recent_play.beatmap.sliders)
            # In Memoriam
            case 277:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.mstars >= 4) and (recent_play.settings.mods_int == 1290)
            # Sanguine
            case 278:
                award_medal = (recent_play.beatmap.id == 131564) and (recent_play.settings.mods_int == 2) and (recent_play.statistics.accuracy >= 92)
            # Not Again
            case 279:
                award_medal = (recent_play.beatmap.beatmapset_id == 1241523) and (recent_play.statistics.count_miss == 1) and (recent_play.statistics.accuracy >= 99)
            # Final Boss
            case 280:
                award_medal = (recent_play.beatmap.id == 3333745) and (recent_play.statistics.accuracy >= 92)
            # Beast Mode
            case 281:
                award_medal = (recent_play.beatmap.id == 2507884) and (recent_play.statistics.accuracy >= 98)
            # Touhou Pack
            case 282:
                pass
            # ginkiha Pack
            case 283:
                pass
            # MUZZ Pack
            case 284:
                pass
            # Deliberation
            case 285:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.mstars >= 6) and (recent_play.settings.mods_int & 256 == 256)
            # Lightless
            case 286:
                award_medal = (recent_play.beatmap.id == 278451) and (recent_play.settings.mods_int & 1024 == 1024)
            # When You See It
            case 287:
                award_medal = (recent_play.beatmap.artist == "xi") and (round(recent_play.statistics.accuracy % 10, 2) == 7.27)
            # Vocaloid Pack
            case 288:
                pass
            # Maduk Pack
            case 289:
                pass
            # Aitsuki Nakuru Pack
            case 290:
                pass
            # 30,000,000 Drum Hits
            case 291:
                award_medal = session.hitcount_taiko >= 30_000_000
            # Catch 20,000,000 fruits
            case 292:
                award_medal = session.hitcount_fruits >= 20_000_000
            # 40,000,000 Keys
            case 293:
                award_medal = session.hitcount_mania >= 40_000_000
            # Ariabl'eyeS Pack
            case 294:
                pass
            # Omoi Pack
            case 295:
                pass
            # Chill Pack
            case 296:
                pass
            # Mortal Coils
            case 297:
                award_medal = check_pack(297, play_history, pack_data, challenge=True)
            # Dark Familiarity
            case 298:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.id == 471598) and (recent_play.settings.mods_int == 40)
            # Creator's Gambit
            case 299:
                # Not implemented
                pass
            # Time Sink
            case 300:
                if len(play_history) < 2: continue
                award_medal = (play_history[-2].beatmap.beatmapset_id == 9215) and (recent_play.beatmap.beatmapset_id == 1537993)
            # Unseen Heights
            case 301:
                award_medal = recent_play.beatmap.mstars >= 100
            # You're Here Forever
            case 302:
                # Not implemented
                pass
            # Hospitality
            case 303:
                # Not implemented
                pass
            # True North
            case 304:
                if len(play_history) < 10: continue
                award_medal = True
                mapsets = set()
                for i in range(1, 11):
                    mapsets.add(play_history[-i].beatmap.beatmapset_id)
                if len(mapsets) != 10:
                    award_medal = False
                for i in range(2, 11):
                    if play_history[-i].beatmap.creator != recent_play.beatmap.creator:
                        award_medal = False
                        break
            # Astronomic (with SV2 conditional)
            case 305:
                award_medal = (recent_play.statistics.full_combo) and (recent_play.beatmap.artist == "II-L") and ((recent_play.beatmap.mstars >= 6) or (recent_play.beatmap.mstars >= 5 and recent_play.settings.mods_int & 536870912 == 536870912))
            # Superfan
            case 306:
                if len(play_history) < 10: continue
                award_medal = True
                mapsets = set()
                for i in range(1, 11):
                    mapsets.add(play_history[-i].beatmap.beatmapset_id)
                if len(mapsets) != 10:
                    award_medal = False
                for i in range(2, 11):
                    if play_history[-i].beatmap.artist != recent_play.beatmap.artist:
                        award_medal = False
                        break
            # Iron Will
            case 307:
                award_medal = check_pack(307, play_history, pack_data, challenge=True)
            # USAO Pack
            case 308:
                pass
            # Rohi Pack
            case 309:
                pass
            # Drum & Bass Pack
            case 310:
                pass
            # Project Loved: Winter 2021
            case 311:
                pass
            # Project Loved: Spring 2022
            case 312:
                pass
            # Project Loved: Summer 2022
            case 313:
                pass
            # Project Loved: Autumn 2022
            case 314:
                pass
            # Project Loved: Winter 2022
            case 315:
                pass
            # Project Loved: Spring 2023
            case 316:
                pass
            # Resurgence
            case 317:
                if len(play_history) < 2: continue
                award_medal = ("ashes" in play_history[-2].beatmap.map_name.lower()) and (recent_play.beatmap.map_name == "Immortal Flame (feat. Anna Yvette)")
            # Clarity
            case 318:
                award_medal = recent_play.beatmap.id == 1480798
            # Autocreation
            case 319:
                award_medal = recent_play.beatmap.artist == recent_play.beatmap.creator
            # Star Power
            case 320:
                if len(play_history) < 2: continue
                award_medal = (play_history[-2].statistics.full_combo) and (play_history[-2].statistics.grade in [0, 2]) and (play_history[-2].settings.mods_int & 16 == 0)
                if award_medal:
                    orig_mods = play_history[-2].settings.mods_int
                    award_medal = (recent_play.statistics.full_combo) and (recent_play.statistics.grade in [0, 2]) and (recent_play.settings.mods_int & 16 == 16) and (recent_play.beatmap.mstars >= 4) and (recent_play.settings.mods_int & orig_mods == orig_mods)
            # Causality
            case 321:
                award_medal = (recent_play.beatmap.id == 2573493) and (recent_play.statistics.accuracy >= 75)
            # Abrogation
            case 322:
                award_medal = (recent_play.beatmap.id == 572525) and (recent_play.statistics.accuracy >= 72)
            # Internment
            case 323:
                if len(play_history) < 3: continue
                award_medal_1 = (play_history[-3].beatmap.id == 3022086) and (play_history[-3].statistics.max_combo == 255) and (play_history[-2].beatmap.id == 3022086) and (play_history[-2].statistics.max_combo == 104) and (recent_play.beatmap.id == 3022086) and (recent_play.statistics.max_combo == 108)
                award_medal_2 = (play_history[-3].beatmap.id == 4052455) and (play_history[-3].statistics.max_combo == 243) and (play_history[-2].beatmap.id == 4052455) and (play_history[-2].statistics.max_combo == 76) and (recent_play.beatmap.id == 4052455) and (recent_play.statistics.max_combo == 133)
                award_medal = award_medal_1 or award_medal_2
            # Anabasis
            case 324:
                award_medal = recent_play.beatmap.id == 2047089
        
        if award_medal:
            session.add_medal(medal.id, recent_play.submit_time)
            medal_stopwatch.add_medal(medal.name, recent_play.submit_time)

    
    print()
    print(session)
