################################################################
# Ricardo
################################################################


################################################################
# Jacek
################################################################


################################################################
# Alberto
################################################################
def run_battle(p1: dict, p2: dict, m1: dict, m2: dict) -> tuple[list[dict], list[dict], str]:
    s1 = stats_dict(p1)
    s2 = stats_dict(p2)

    p1_types = [t["type"]["name"] for t in p1["types"]]
    p2_types = [t["type"]["name"] for t in p2["types"]]

    hp1 = s1["hp"]
    hp2 = s2["hp"]

    log = []
    hp_hist = [
        {"round": 0, "pokemon": p1["name"].title(), "hp": hp1},
        {"round": 0, "pokemon": p2["name"].title(), "hp": hp2},
    ]

    def first_attacker() -> str:
        if s1["speed"] > s2["speed"]:
            return "p1"
        if s2["speed"] > s1["speed"]:
            return "p2"
        return random.choice(["p1", "p2"])

    for rnd in range(1, MAX_ROUNDS + 1):
        if hp1 <= 0 or hp2 <= 0:
            break

        first = first_attacker()
        order = [first, "p2" if first == "p1" else "p1"]

        for who in order:
            if hp1 <= 0 or hp2 <= 0:
                break

            if who == "p1":
                atk_p, def_p = p1, p2
                atk_stats, def_stats = s1, s2
                def_types = p2_types
                move = m1
                defender_hp = hp2
            else:
                atk_p, def_p = p2, p1
                atk_stats, def_stats = s2, s1
                def_types = p1_types
                move = m2
                defender_hp = hp1

            move_name = move["name"].replace("-", " ").title()
            power = int(move["power"]) if move["power"] is not None else 0
            acc = move["accuracy"]
            acc_val = 100 if acc is None else int(acc)
            dmg_class = move["damage_class"]
            mtype = move["type"]

            atk_stat, def_stat = pick_atk_def(atk_stats, def_stats, dmg_class)
            eff = effectiveness_multiplier(mtype, def_types)

            hit = random.random() < (acc_val / 100.0)
            if not hit:
                damage = 0
                result = "Missed"
            else:
                base_dmg = (2 * LEVEL / 5 + 2) * power
                stat_ratio = atk_stat / max(1, def_stat)
                damage = int((base_dmg * stat_ratio / 50 + 2) * eff)
                result = "Hit"

            defender_hp_after = max(0, defender_hp - damage)

            if who == "p1":
                hp2 = defender_hp_after
            else:
                hp1 = defender_hp_after

            log.append({
                "Round": rnd,
                "Attacker": atk_p["name"].title(),
                "Move": move_name,
                "Move Type": mtype,
                "Class": dmg_class,
                "Power": power,
                "Accuracy": acc_val,
                "Effectiveness": eff,
                "Damage": damage,
                "Defender": def_p["name"].title(),
                "Defender HP": defender_hp_after,
                "Result": result,
            })

        hp_hist.append({"round": rnd, "pokemon": p1["name"].title(), "hp": hp1})
        hp_hist.append({"round": rnd, "pokemon": p2["name"].title(), "hp": hp2})

    if hp1 <= 0 and hp2 <= 0:
        winner = "Draw (double KO)"
    elif hp2 <= 0:
        winner = p1["name"].title()
    elif hp1 <= 0:
        winner = p2["name"].title()
    else:
        winner = "Draw (100-round cap)"

    return log, hp_hist, winner
################################################################
# Shadi
################################################################


################################################################
# Mateus 
################################################################


################################################################
# Blanca
################################################################