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
