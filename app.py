import streamlit as st

import numpy as np
import pandas as pd
from market_value_predictor.utils import get_player_id, get_player_image

from PIL import Image

player_name = st.text_input('Player', 'Player')

pic_path = get_player_image(get_player_id(player_name))
image = Image.open(pic_path)
st.image(image, caption='test', use_column_width=False)
