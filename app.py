import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import plotly.express as px  

st.set_page_config(page_title="Статистика Центральной Азии", layout="wide")


st.title("Анализ статистики Центральной Азии")


file_path = "CentralAsia.xlsx"  
df_pandas = pd.read_excel(file_path)


df_pandas[['country', 'year']] = df_pandas['year'].str.split('_', expand=True)
df_pandas['year'] = pd.to_numeric(df_pandas['year'])

country_mapping = {
    'Kazakhstan': 'Казахстан',
    'KGZ': 'Кыргызстан',
    'TAIJ': 'Таджикистан',
    'UZB': 'Узбекистан'
}

df_pandas['country'] = df_pandas['country'].replace(country_mapping)
df_pandas = df_pandas.rename(columns={'country': 'Страна'})


countries = df_pandas['Страна'].unique().tolist()
selected_countries = st.multiselect("Выберите страны для отображения:", countries, default=countries)


year_range = st.slider("Выберите диапазон лет:", min_value=int(df_pandas['year'].min()), 
                        max_value=int(df_pandas['year'].max()), value=(2014, 2017))


metrics_mapping = {
    'F_mod_sev_ad': 'Модиф. тяжесть прод. безоп. среди взросл.',
    'F_sev_ad': 'Тяжесть прод. безоп. среди взросл.',
    'F_mod_sev_child': 'Модиф. тяжесть прод. безоп. среди детей',
    'F_sev_child': 'Тяжесть прод. безоп. среди детей',
    'Pop_mod_sev_tot': 'Общая модифиц. тяжесть прод. безоп.',
    'Pop_sev_tot': 'Общая тяжесть прод. безоп.'
}

metrics = list(metrics_mapping.keys())
selected_metric = st.selectbox("Выберите показатель для визуализации:", metrics, format_func=lambda x: metrics_mapping[x])


filtered_data = df_pandas[(df_pandas['Страна'].isin(selected_countries)) & 
                           (df_pandas['year'].between(year_range[0], year_range[1]))]

if not filtered_data.empty:
   
    average_severity = filtered_data[selected_metric].mean()
    st.metric(label="Средняя тяжесть", value=f"{average_severity:.2f}")

   
    st.write("Статистика по выбранным данным:")
    stats = filtered_data.groupby('Страна')[selected_metric].agg(['mean', 'min', 'max']).reset_index()
    stats.columns = ['Страна', 'Среднее', 'Минимум', 'Максимум']  
    st.write(stats)

    
    plt.style.use('ggplot')

    
    tab1, tab2, tab3, tab4 = st.tabs(["Линейный график", "Столбчатая диаграмма", "Ящичный график", "Тепловая карта"])

    with tab1:
        st.write("График ниже показывает изменение {} по годам для выбранных стран.".format(metrics_mapping[selected_metric]))
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=filtered_data, x='year', y=selected_metric, hue='Страна', marker='o', linewidth=2.5)
        plt.xticks(filtered_data['year'].unique(), rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.title('Изменение {} по годам'.format(metrics_mapping[selected_metric]), fontsize=16, weight='bold', color='darkblue')
        plt.xlabel('Год', fontsize=12, color='darkgreen')
        plt.ylabel(metrics_mapping[selected_metric], fontsize=12, color='darkgreen')
        plt.legend(title='Страна', fontsize=10, title_fontsize=12, loc='upper right')
        plt.grid(True, which='both', linestyle='--', linewidth=0.7, color='gray', alpha=0.7)
        plt.tight_layout()
        st.pyplot(plt)

    with tab2:
        st.write("Столбчатая диаграмма для сравнения {} по странам.".format(metrics_mapping[selected_metric]))
        plt.figure(figsize=(12, 6))
        sns.barplot(data=filtered_data, x='year', y=selected_metric, hue='Страна', ci=None)
        plt.title('Сравнение {} по странам'.format(metrics_mapping[selected_metric]), fontsize=16, weight='bold', color='darkblue')
        plt.xlabel('Год', fontsize=12, color='darkgreen')
        plt.ylabel(metrics_mapping[selected_metric], fontsize=12, color='darkgreen')
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.legend(title='Страна', fontsize=10, title_fontsize=12, loc='upper right')
        st.pyplot(plt)

    with tab3:
        st.write("Ящичный график для отображения распределения {} по странам.".format(metrics_mapping[selected_metric]))
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=filtered_data, x='Страна', y=selected_metric, palette='Set2')
        plt.title('Распределение {} по странам'.format(metrics_mapping[selected_metric]), fontsize=16, weight='bold', color='darkblue')
        plt.xlabel('Страна', fontsize=12, color='darkgreen')
        plt.ylabel(metrics_mapping[selected_metric], fontsize=12, color='darkgreen')
        plt.xticks(rotation=45, fontsize=10)
        plt.tight_layout()
        st.pyplot(plt)

    with tab4:
        st.write("Тепловая карта корреляций между метриками.")
        corr = df_pandas[metrics].corr()
        plt.figure(figsize=(12, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
        plt.title('Корреляция между метриками', fontsize=16, weight='bold', color='darkblue')
        plt.tight_layout()
        st.pyplot(plt)

   
    st.write("Анимированный график изменения {} по годам.".format(metrics_mapping[selected_metric]))
  
    fig = px.line(filtered_data, x='year', y=selected_metric, color='Страна', 
                  title='Анимированный график изменения {} по годам'.format(metrics_mapping[selected_metric]), 
                  animation_frame='year', 
                  range_y=[filtered_data[selected_metric].min(), filtered_data[selected_metric].max()],
                  labels={'year': 'Год', selected_metric: metrics_mapping[selected_metric]})
    st.plotly_chart(fig, use_container_width=True)

    
    st.write("Карта с расположением стран:")
    map_data = pd.DataFrame({
        'Страна': ['Казахстан', 'Кыргызстан', 'Таджикистан', 'Узбекистан'],
        'Лат': [48.0196, 41.2044, 38.8610, 41.3775],
        'Лон': [66.9237, 74.7661, 74.5698, 64.5850],
        'Метрика': [average_severity] * 4  
    })

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=39.5,
            longitude=66.9,
            zoom=3,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[Лон, Лат]',
                get_color='[255, 0, 0]',
                get_radius=50000,
                pickable=True,
            ),
        ],
        tooltip={
            "text": "{Страна}\nСредняя тяжесть: {Метрика:.2f}\n{Лат}, {Лон}"
        },
    ))
else:
    st.error("Не удалось получить данные для выбранных стран.")
