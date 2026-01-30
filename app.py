import streamlit as st
import pandas as pd
import pydeck as pdk

df_point = pd.read_csv('prefecture_point.csv')
df_point['lat'] = pd.to_numeric(df_point['lat'], errors="coerce")
df_point['lon'] = pd.to_numeric(df_point['lon'], errors="coerce")

df_population = pd.read_csv('FEH_00200521_260127162349.csv',
                 skiprows=14,
                 encoding="utf-8")

#列の抽出
columns_needed = ['全国～人口50万以上の市','0歳','1歳', '2歳', '3歳', '4歳', '5歳', '6歳', '7歳', '8歳', '9歳', '10歳', '11歳','12歳', '13歳', '14歳']
df_population = df_population[columns_needed]

#数値化
for age in range(15):
  df_population[str(age) + '歳'] = df_population[str(age) + '歳'].str.replace(",", "").astype(int)

#人口合計の計算と新しい列の作成
df_population['age_0_14'] = df_population[[str(age) + '歳' for age in range(15)]].sum(axis=1)

#dataframeの変更と列の改名
df_population.rename(columns={'全国～人口50万以上の市':'都道府県'}, inplace=True)
df_population.drop(index=0,inplace=True)
df_population['age_0_14'] = pd.to_numeric(df_population['age_0_14'], errors="coerce")
df_popu_child = pd.merge(df_point, df_population[['都道府県','age_0_14']], on="都道府県", how="left")


#pydeck Layerの作成
layer = pdk.Layer(
  "ColumnLayer",
  df_popu_child,
  get_position=['lon', 'lat'],
  get_elevation='age_0_14',
  elevation_scale=0.5,
  radius=20000,
  get_fill_color=[255, 100, 100],
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

map_population = pdk.Deck(
  layers=[layer],
  initial_view_state=view_state
  )

st.dataframe(df_population, width=800, height=220)
st.dataframe(df_popu_child)
st.pydeck_chart(map_population)
