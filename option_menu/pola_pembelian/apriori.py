import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules

@st.cache_data
def data_apriori(groceries, start_date, end_date):
    st.header("Pola Pembelian")
    
    # Hitung jumlah hari yang dipilih
    days_selected = (end_date - start_date).days + 1
    day_text = "day" if days_selected == 1 else "days"
    st.caption(f"Based on data from {start_date} to {end_date} ({days_selected} {day_text}).")
    
    # Renaming the columns to simple words
    groceries.rename(columns={'NO.TRANSAKSI': 'id', 'DESCRIPTION_CLEANED': 'item'}, inplace=True)

    # Creating temporary data which has quantity purchased column
    temp = groceries.copy()
    temp['qty_purchased'] = groceries['id'].map(groceries['id'].value_counts())

    # Creating sparse matrix
    basket = (temp.groupby(['id', 'item'])['qty_purchased']
              .sum().unstack().reset_index().fillna(0)
              .set_index('id'))

    # Encoding the quantity purchased
    def encode(x):
        '''Encoding the quantity of products with 0s and 1s
        0: when qty is less than or equal to 0
        1: when qty is greater than or equal to 1'''
        return 1 if x >= 1 else 0

    # Applying on our data
    basket_sets = basket.applymap(encode)
    return basket_sets

@st.cache_data
def apriori_algorithm(basket_sets):
    st.markdown(
        "<div style='font-weight: bold; font-size: 18px;'>Hasil Rules Items</div>",
        unsafe_allow_html=True
    )
    # Apriori
    frequent_itemsets = apriori(basket_sets, min_support=0.001, use_colnames=True, low_memory=True)

    # Association rules - using lift
    rules = association_rules(frequent_itemsets, num_itemsets=len(frequent_itemsets))

    # Customizable function to change the lift and confidence
    def rules_mod(lift, confidence):
        '''rules_mod is a function to control the rules 
        based on lift and confidence threshold'''
        return rules[(rules['lift'] >= lift) & (rules['confidence'] >= confidence)]

    return rules_mod(1, 0.5)

def apriori_visual(rules):
    with st.expander("Visualisasi"):
        # Slider untuk memilih jumlah aturan yang akan ditampilkan
        rules_to_show = st.slider(
            "Pilih jumlah rules untuk divisualisasikan:",
            min_value=1,
            max_value=len(rules),
            value=3,  # Nilai default
            step=1
        )

        G1 = nx.DiGraph()
        color_map = []
        # N = 50  # Membatasi jumlah warna acak
        # colors = np.random.rand(N)  # Array warna acak
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'pink', 'brown', 'gray', 'magenta']
        strs = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11']

        for i in range(rules_to_show):
            # Menambahkan node untuk setiap rule
            rule_node = "R" + str(i)
            G1.add_node(rule_node)

            # Menambahkan edges untuk antecedents (premis) -> rule
            for a in rules.iloc[i]['antecedents']:
                G1.add_node(a)  # Menambahkan node antecedent
                G1.add_edge(a, rule_node, color=colors[i], weight=2)  # Menghubungkan antecedent ke rule

            # Menambahkan edges untuk rule -> consequents (konsekuen)
            for c in rules.iloc[i]['consequents']:
                G1.add_node(c)  # Menambahkan node consequent
                G1.add_edge(rule_node, c, color=colors[i], weight=2)  # Menghubungkan rule ke consequent

        # Menentukan warna node
        for node in G1:
            if node in strs:  # Jika node adalah rule node (misalnya R0, R1, ...)
                color_map.append('lime')
            else:  # Jika node adalah antecedent atau consequent
                color_map.append('yellow')

        # Menentukan warna dan bobot edge
        edges = G1.edges()
        edge_colors = [G1[u][v]['color'] for u, v in edges]
        edge_weights = [G1[u][v]['weight'] for u, v in edges]

        # Menata posisi node menggunakan spring_layout
        pos = nx.spring_layout(G1, k=16, seed=42)

        plt.figure(figsize=(15, 8))
        plt.gca().set_facecolor("#F0F2F6")

        # Menggambar graph
        nx.draw(
            G1, pos, node_color=color_map, edge_color=edge_colors,
            width=edge_weights, font_size=12, with_labels=False
        )

        # Menambahkan label node (rule, antecedent, consequent)
        for p in pos:
            pos[p][1] += 0  # Mengangkat posisi label agar tidak menutupi node
        nx.draw_networkx_labels(G1, pos)
        st.pyplot(plt.gcf())

def analyze_rules(rules):
    st.markdown(
        "<div style='font-weight: bold; font-size: 18px;'>Analisis</div>",
        unsafe_allow_html=True
    )
    # Jumlah total rules
    total_rules = len(rules)

    # Rata-rata metrik penting
    avg_support = rules['support'].mean()
    avg_confidence = rules['confidence'].mean()
    avg_lift = rules['lift'].mean()

    # Rule dengan Lift tertinggi
    best_rule = rules.iloc[rules['lift'].idxmax()]
    rule_analysis = (
        f"Jika membeli **{', '.join(best_rule['antecedents'])}**, "
        f"kemungkinan besar juga akan membeli **{', '.join(best_rule['consequents'])}**.\n"
        f"- Lift: {best_rule['lift']:.2f}\n"
        f"- Confidence: {best_rule['confidence']:.2%}\n"
        f"- Support: {best_rule['support']:.4f}\n"
    )

    # Kesimpulan
    kesimpulan = (
        f"Dari analisis yang dilakukan, ditemukan {total_rules} rules dengan rata-rata dukungan (support) sebesar "
        f"{avg_support:.4f}, kepercayaan (confidence) sebesar {avg_confidence:.2%}, dan pengaruh (lift) rata-rata sebesar "
        f"{avg_lift:.2f}. Sebagian besar rules menunjukkan hubungan {'positif (Lift > 1)' if avg_lift > 1 else 'negatif atau lemah (Lift <= 1)'}. "
        f"Kepercayaan rata-rata {'cukup tinggi sehingga aturan-aturan dapat diandalkan' if avg_confidence > 0.5 else 'rendah sehingga aturan-aturan mungkin kurang relevan'}. "
        f"Analisis ini dapat membantu menentukan strategi pemasaran seperti menyusun bundling produk atau pengaturan rak toko dengan memprioritaskan rules yang memiliki Lift dan Confidence tinggi."
    )

    # Gabungkan semua analisis ke dalam elemen st.success
    st.success(
        f"**Jumlah total rules yang ditemukan:** {total_rules}\n\n"
        f"**Rata-rata Metrik Penting**\n"
        f"- Support (Dukungan rata-rata): {avg_support:.4f}\n"
        f"- Confidence (Kepercayaan rata-rata): {avg_confidence:.2%}\n"
        f"- Lift (Pengaruh rata-rata): {avg_lift:.2f}\n\n"
        f"**Rule dengan pengaruh tertinggi (Lift)**\n\n"
        f"{rule_analysis}\n\n"
        f"**Kesimpulan:** {kesimpulan}"
    )
