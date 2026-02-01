import streamlit as st
import pandas as pd
import pydeck as pdk

st.title('全国の子供人口となんたらかんたら')

st.header('本アプリについて')
st.write('本アプリは、全国の子供人口と保育所等の施設数から、***都道府県に合わせた子育て支援***について分析することを目的として作られています。')
st.write('選択されたデータセットを***日本地図上に立体的に表示***することで、視覚的に地域比較を行うことができます。')

st.header('表示選択')

st.write('選択できるものは以下の通りです。')
st.write('1. 全国の都道府県別0歳～14歳の人口')
st.write('2. 全国の都道府県別施設数')
st.caption('施設数は、保育所(幼保連携型認定こども園,保育所型認定こども園,保育所),小学校,中学校の施設合計数です。', help='都道府県の順番に規則性がなくなります。')
st.write('3. 全国の都道府県別子供収容指標')
st.caption('本指標は、0歳～14歳を子供とし、子供人口を施設数で割ったものです。1施設あたりの子供収容人数を表します。', help='本アプリでは、保育所、小学校、中学校に対応する年齢について区別をしておらず、0歳～14歳人口を施設数で割っているため、正確な収容人数ではありません。')
st.caption('※使用している人口と施設数のデータは2020年のものです。', help='本アプリでは人口のデータを国勢調査から取得しました。最新の国勢調査が2020年(令和2年)のものであったため、全てを2020年のデータで統一しています。')
select = st.selectbox('表示するデータセットを選択してください。'
                      ,['1. 子供人口', '2. 施設数', '3. 収容指標'])

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


# <<保育所・小学校・中学校>>
df_count_nur = pd.read_csv('count_nur.csv')
df_count_elm = pd.read_csv('count_elmsch.csv')
df_count_jni = pd.read_csv('count_jnisch.csv')

df_count = pd.concat([df_count_nur, df_count_elm, df_count_jni], ignore_index=True)
df_count = df_count.groupby("都道府県", as_index=False)["count"].sum()
df_fac_count = pd.merge(df_point, df_count, on="都道府県", how="left")


# <<1施設当たりの子供収容指標>>
df_score = pd.merge(df_pop_child, df_count, on="都道府県", how="left")
df_score['cld_per_fac'] = df_score['age_0_14'] / df_score['count']


if select == '1. 子供人口':
    data = df_pop_child
    value = 'age_0_14'
    color = [255, 100, 100]
elif select == '2. 施設数':
    data = df_fac_count
    value = 'count'
    color = [100, 100, 255]

#pydeck Layerの作成
view_state = pdk.ViewState(
  latitude=36.0,
  longitude=138.0,
  zoom=4.8,
  bearing=0,
  pitch=45
  )

if select == '1. 子供人口' or select == '2. 施設数':

  layer = pdk.Layer(
    "ColumnLayer",
    data,
    get_position=['lon', 'lat'],
    get_elevation=value,
    elevation_scale=0.5,
    radius=20000,
    get_fill_color=color,
    pickable=True,
    extruded=True
  )

  map = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state
    )
  
else:
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

  map_score = pdk.Deck(
    layers=[layer1, layer2],
    initial_view_state=view_state
    )

if select == '1. 子供人口':
    option1 = st.checkbox('年齢別表示', help='0歳から14歳までの各人口を表示します。')
    if option1 == True:
        st.dataframe(df_population)
    elif option1 == False:
        st.dataframe(df_pop_child[['都道府県', 'age_0_14']])
    st.pydeck_chart(map)
elif select == '2. 施設数':
    st.dataframe(df_count)
    st.pydeck_chart(map)
else:
    st.dataframe(df_score[['都道府県', 'age_0_14', 'count', 'cld_per_fac']])
    st.pydeck_chart(map_score)