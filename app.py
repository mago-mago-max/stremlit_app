import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.title('都道府県別　子供人口/教育・保育施設数')

st.divider()

#説明
st.header('本アプリについて')
st.write('本アプリは、全国の子供人口と教育・保育施設数から、***都道府県に合わせた子育て支援***について分析することを目的として作られています。')
st.write('選択されたデータセットを***日本地図上に立体的に表示***することで、視覚的に地域比較を行うことができます。')

st.divider()

#表示できるデータセットの説明
st.header('表示選択')
st.write('選択できるものは以下の通りです。')
st.write('1. 都道府県別　0歳～14歳の人口')
st.caption('全国の0歳~14歳の人口を年齢別/合計の2通りで都道府県別に表示します。')
st.write('2. 都道府県別　施設数')
st.caption('全国の教育・保育施設数を都道府県別に表示します。')
st.caption('教育・保育施設数は、保育所(幼保連携型認定こども園,保育所型認定こども園,保育所),小学校,中学校の合計数です。', help='都道府県の順番に規則性がなくなります。')
st.write('3. 都道府県別　子供収容指標')
st.caption('子供収容指標の数値を表で表示し、0歳~14歳の人口合計と施設数を同時に地図上に表示します。また、子供人口に対する施設数を散布図で表示します。')
st.caption('本指標は、0歳～14歳を子供とし、子供人口を施設数で割ったものです。1施設あたりの子供収容人数を表します。', help='本アプリでは、保育所、小学校、中学校に対応する年齢について区別をしておらず、0歳～14歳人口を施設数で割っているため、正確な収容人数ではありません。')
st.caption('※使用している人口と施設数のデータは2020年のものです。', help='本アプリでは人口のデータを国勢調査から取得しました。最新の国勢調査が2020年(令和2年)のものであったため、全てを2020年のデータで統一しています。')
st.caption('※地図の操作方法については、「地図」と書かれた右側にある？マークにカーソルを合わせることで確認できます。')
select = st.selectbox('表示するデータセットを選択してください。'
                      ,['1. 子供人口', '2. 施設数', '3. 収容指標'])

df_point = pd.read_csv('prefecture_point.csv')
df_point['lat'] = pd.to_numeric(df_point['lat'], errors="coerce")
df_point['lon'] = pd.to_numeric(df_point['lon'], errors="coerce")

# <<人口>>
df_population = pd.read_csv('FEH_00200521_260127162349.csv',
                 skiprows=14,
                 encoding="utf-8")

pop_columns_needed = ['全国～人口50万以上の市','0歳','1歳', '2歳', '3歳', '4歳', '5歳', '6歳', '7歳', '8歳', '9歳', '10歳', '11歳','12歳', '13歳', '14歳']
df_population = df_population[pop_columns_needed]  #列の抽出
for age in range(15):  #数値化
  df_population[str(age) + '歳'] = df_population[str(age) + '歳'].str.replace(",", "").astype(int)
df_population['age_0_14'] = df_population[[str(age) + '歳' for age in range(15)]].sum(axis=1)   #人口合計の計算と新しい列の作成
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
  
  #散布図
  fig = px.scatter(
     df_score,
    x='age_0_14',
    y='count',
    labels={'age_0_14':'0歳~14歳人口 (人)','count':'教育・保育施設数 (か所)'},
    )

map_caption = '左クリック&ドラッグで移動、右クリック&ドラッグで視点移動、スクロールで拡大・縮小'

st.divider()

if select == '1. 子供人口':
    st.subheader('表：都道府県別　子供人口')
    st.write('各項目について')
    st.write('都道府県：都道府県名を示しています。')
    st.write('0歳,1歳,...,14歳：各年齢に対応する人口を示しています。(単位：人)')
    st.write('age_0_14：:歳から14歳の人口の合計を示しています。(単位：人)')
    option = st.checkbox('年齢別表示', help='0歳から14歳までの各人口を表に表示します。')
    if option == True:
        st.dataframe(df_population)
    elif option == False:
        st.dataframe(df_pop_child[['都道府県', 'age_0_14']])
    st.subheader('地図', help=map_caption)
    st.pydeck_chart(map)
    st.divider()
    st.write('都市圏の子供人口が多いことが分かる。最小が鳥取県の68,330人、最大が東京都の15,668,40人と、約23倍差がある。')
elif select == '2. 施設数':
    st.subheader('表：都道府県別　施設数')
    st.write('各項目について')
    st.write('都道府県：都道府県名を示しています。')
    st.write('count：施設数を示しています。(単位：か所)')
    st.dataframe(df_count)
    st.subheader('地図', help=map_caption)    
    st.pydeck_chart(map)
    st.divider()
    st.write('都道府県の面積に関係なく、都市圏の施設数が多いことが分かる。')
else:
    st.subheader('表：都道府県別　子供収容指標')
    st.write('各項目について')
    st.write('都道府県：都道府県名を示しています。')
    st.write('age_0_14:0歳から14歳の人口の合計を示しています。(単位：人)')
    st.write('count：施設数を示しています。(単位：か所)')
    st.write('cld_per_fac：子供人口を施設数で割った結果を示しています。(単位：なし)')
    st.dataframe(df_score[['都道府県', 'age_0_14', 'count', 'cld_per_fac']])
    st.subheader('地図', help=map_caption)
    st.pydeck_chart(map_score)
    st.subheader('散布図：都道府県別 子供人口と施設数')
    st.plotly_chart(fig)
    st.divider()
    st.write('子供人口の多い都道府県ほど、施設が多いことが分かる。埼玉県や千葉県は子供収容指標が7を超えており、他の県と比べて教育・保育施設が圧倒的に圧迫されているのではないかと推察される。子供人口が一番多い東京は、指標が5.4と、全国で比べた場合は平均あたりであった。')
    st.write('指標が6を超える都道府県に関しては、教育現場が圧迫されており、子供を育てる環境づくりが不十分であると考えられる。よって、子供人口を増やすための子育て支援ではなく、子供を育てる環境を充実させる方向での子育て支援をするべきではないだろうか。')