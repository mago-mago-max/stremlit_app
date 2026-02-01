import streamlit as st
import pandas as pd
import pydeck as pdk

df_point = pd.read_csv('prefecture_point.csv')
df_point['lat'] = pd.to_numeric(df_point['lat'], errors="coerce")
df_point['lon'] = pd.to_numeric(df_point['lon'], errors="coerce")


# <<人口>>
df_population = pd.read_csv('FEH_00200521_260127162349.csv',
                 skiprows=14,
                 encoding="utf-8")

#列の抽出
pop_columns_needed = ['全国～人口50万以上の市','0歳','1歳', '2歳', '3歳', '4歳', '5歳', '6歳', '7歳', '8歳', '9歳', '10歳', '11歳','12歳', '13歳', '14歳']
df_population = df_population[pop_columns_needed]

#数値化
for age in range(15):
  df_population[str(age) + '歳'] = df_population[str(age) + '歳'].str.replace(",", "").astype(int)

#人口合計の計算と新しい列の作成
df_population['age_0_14'] = df_population[[str(age) + '歳' for age in range(15)]].sum(axis=1)

#dataframeの変更と列の改名
df_population.rename(columns={'全国～人口50万以上の市':'都道府県'}, inplace=True)
df_population.drop(index=0,inplace=True)
df_population['age_0_14'] = pd.to_numeric(df_population['age_0_14'], errors="coerce")
df_pop_child = pd.merge(df_point, df_population[['都道府県','age_0_14']], on="都道府県", how="left")

# #pydeck Layerの作成
# layer = pdk.Layer(
#   "ColumnLayer",
#   df_pop_child,
#   get_position=['lon', 'lat'],
#   get_elevation='age_0_14',
#   elevation_scale=0.5,
#   radius=20000,
#   get_fill_color=[255, 100, 100],
#   pickable=True,
#   extruded=True
# )

# view_state = pdk.ViewState(
#   latitude=36.0,
#   longitude=138.0,
#   zoom=4.8,
#   bearing=0,
#   pitch=45
# )

# map_population = pdk.Deck(
#   layers=[layer],
#   initial_view_state=view_state
#   )

# st.dataframe(df_population, width=800, height=220)
# st.dataframe(df_pop_child)
# st.pydeck_chart(map_population)


# <<保育所・小学校・中学校>>
df_count_nur = pd.read_csv('count_nur.csv')
df_count_elm = pd.read_csv('count_elmsch.csv')
df_count_jni = pd.read_csv('count_jnisch.csv')

df_count = pd.concat([df_count_nur, df_count_elm, df_count_jni], ignore_index=True)
df_count = df_count.groupby("都道府県", as_index=False)["count"].sum()
df_fac_count = pd.merge(df_point, df_count, on="都道府県", how="left")

# #pydeck Layerの作成
# layer = pdk.Layer(
#   "ColumnLayer",
#   df_fac_count,
#   get_position=['lon', 'lat'],
#   get_elevation='count',
#   elevation_scale=0.5,
#   radius=20000,
#   get_fill_color=[100, 100, 255],
#   pickable=True,
#   extruded=True
# )

# view_state = pdk.ViewState(
#   latitude=36.0,
#   longitude=138.0,
#   zoom=4.8,
#   bearing=0,
#   pitch=45
# )

# map_count = pdk.Deck(
#   layers=[layer],
#   initial_view_state=view_state
#   )

# st.dataframe(df_count)
# st.pydeck_chart(map_count)


# 1施設当たりの子供の数指標
# st.table(df_pop_child)
# st.table(df_count)

df_score = pd.merge(df_pop_child, df_count, on="都道府県", how="left")
df_score['cld_per_fac'] = df_score['age_0_14'] / df_score['count']

#pydeck Layerの作成
layer1 = pdk.Layer(
  "ColumnLayer",
  df_score,
  get_position=['lon-0.1', 'lat'],
  get_elevation='age_0_14',
  elevation_scale=0.5,
  radius=10000,
  get_fill_color=[255, 100, 100],
  pickable=True,
  extruded=True
)

layer2 = pdk.Layer(
  "ColumnLayer",
  df_score,
  get_position=['lon+0.1', 'lat'],
  get_elevation='count',
  elevation_scale=0.5,
  radius=10000,
  get_fill_color=[100, 100, 255],
  pickable=True,
  extruded=True
)

view_state = pdk.ViewState(
  latitude=36.0,
  longitude=138.0,
  zoom=4.8,
  bearing=0,
  pitch=45
)

map_score = pdk.Deck(
  layers=[layer1, layer2],
  initial_view_state=view_state
  )

st.dataframe(df_score)
st.pydeck_chart(map_score)
