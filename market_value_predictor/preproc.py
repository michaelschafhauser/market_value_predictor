import pandas as pd

def manual_encoding(df, column_name):
    df_encode = df[column_name].str.get_dummies(
        sep=",")

    init_cols_player_positions = list(df_encode.columns)

    trans_cols_player_positions = []
    for elem in init_cols_player_positions:
        trans_cols_player_positions.append(elem.strip())

    df_encode = df_encode.rename(columns=dict(
        zip(init_cols_player_positions, trans_cols_player_positions)))

    df_encode = df_encode.groupby(lambda x: x, axis=1).sum()

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


def reduce_number_of_classes(df, column_name, min_count):
    temp_df = pd.DataFrame(
        df[column_name].value_counts()).reset_index().rename(
            columns={
                "index": column_name,
                column_name: "count"
            })

    temp_list = []

    for i, elem in enumerate(list(temp_df["count"])):
        if elem > min_count:
            temp_list.append(list(temp_df[column_name])[i])
        else:
            temp_list.append("other")

    temp_df[f"{column_name}_cleaned"] = temp_list

    temp_df = temp_df.drop(columns="count")

    df = df.merge(temp_df, on=column_name,
                              how="left")#.drop(columns=column_name)

    return df
