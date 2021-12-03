def manual_encoding(df, column_name):
    df_encode = df[column_name].str.get_dummies(
        sep=",")

    init_cols_player_positions = list(df_encode.columns)

    trans_cols_player_positions = []
    for elem in init_cols_player_positions:
        trans_cols_player_positions.append(elem.strip())

    df_encode = df_encode.rename(columns=dict(
        zip(init_cols_player_positions, trans_cols_player_positions)))

    df_encode_encoded = df_encode.add_prefix(f"{column_name}_")

    df = df.join(df_encode_encoded)

    df = df.drop(columns=[column_name])

    return df


def cluster_team_position(df):
    attack = ["ST", "LS", "LW", "RS", "RW", "RF", "LF", "CF"]
    mid = [
        "LCM", "RM", "CB", "CAM", "LM", "CM", "CDM", "RCM", "LCM", "RDM", "LDM",
        "RAM", "LAM"
    ]
    defense = ["RCB", "LCB", "CB", "RB", "LB", "RWB", "LWB"]
    goal = ["GK"]
    sub = ["SUB", "RES"]

    df["position_cluster"] = df.team_position.map(
        lambda x: "attack" if x in attack else "mid" if x in mid else "defense"
        if x in defense else "goal" if x in goal else "sub"
        if x in sub else "nan")

    return df
