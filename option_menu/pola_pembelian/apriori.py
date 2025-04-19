import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import cm, colors 
import networkx as nx
import numpy as np
import pandas as pd
from collections import Counter
from mlxtend.frequent_patterns import apriori, association_rules

@st.cache_data
def data_apriori(groceries, start_date, end_date):
    st.header("Pola Pembelian")
    
    # Hitung jumlah hari yang dipilih
    days_selected = (end_date - start_date).days + 1
    day_text = "day" if days_selected == 1 else "days"
    st.caption(f"Based on data from {start_date} to {end_date} ({days_selected} {day_text}).")

    # Creating temporary data which has quantity purchased column
    temp = groceries.copy()
    temp['qty_purchased'] = groceries['NO TRANSAKSI'].map(groceries['NO TRANSAKSI'].value_counts())

    # Creating sparse matrix
    basket = (temp.groupby(['NO TRANSAKSI', 'NAMA BARANG'])['qty_purchased']
              .sum().unstack().reset_index().fillna(0)
              .set_index('NO TRANSAKSI'))

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
    # Apriori
    frequent_itemsets = apriori(basket_sets, min_support=0.0001, use_colnames=True, low_memory=True)

    # Association rules - using lift
    rules = association_rules(frequent_itemsets, num_itemsets=len(frequent_itemsets))

    # Customizable function to change the lift and confidence
    def rules_mod(lift, confidence):
        '''rules_mod is a function to control the rules 
        based on lift and confidence threshold'''
        filtered_rules = rules[(rules['lift'] >= lift) & (rules['confidence'] >= confidence)]
        return filtered_rules.reset_index(drop=True)

    return rules_mod(1, 1).sort_values(by='lift', ascending=False).reset_index(drop=True)

def apriori_visual(rules, rules_to_show):
    G1 = nx.DiGraph()
    color_map = []

    cmap = cm.get_cmap('Greens')
    edge_palette = [
        colors.rgb2hex(cmap(i)) for i in np.linspace(0.4, 0.9, rules_to_show)
    ] 

    edge_index = 0
    strs = [f'R{i}' for i in range(len(rules))]

    for i in range(rules_to_show):
        rule_node = f"R{i}"
        G1.add_node(rule_node)

        current_edge_color = edge_palette[edge_index % len(edge_palette)]
        edge_index += 1

        for a in rules.iloc[i]['antecedents']:
            G1.add_node(a)
            G1.add_edge(a, rule_node, color=current_edge_color, weight=3)

        for c in rules.iloc[i]['consequents']:
            G1.add_node(c)
            G1.add_edge(rule_node, c, color=current_edge_color, weight=3)

    for node in G1:
        color_map.append('yellow' if node in strs else '#b0b0b0')

    edges = G1.edges()
    edge_colors = [G1[u][v]['color'] for u, v in edges]
    edge_weights = [G1[u][v]['weight'] for u, v in edges]

    pos = nx.spring_layout(G1, k=16, seed=42)
    plt.figure(figsize=(15, 8))
    plt.gca().set_facecolor("#F0F2F6")

    node_sizes = [900 if node in strs else 600 for node in G1]

    nx.draw(
        G1, pos, node_color=color_map, edge_color=edge_colors,
        width=edge_weights, font_size=16, with_labels=False, arrowsize=25,
        node_size=node_sizes
    )

    for p in pos:
        pos[p][1] += 0
    nx.draw_networkx_labels(G1, pos)
    st.pyplot(plt.gcf())

def analyze_rules(rules, rules_to_show):
    with st.expander("Detail Analisis"):
        st.caption("Dari Line Graph di atas, dapat dilihat beberapa kecenderungan menarik dari pelanggan: \n")
        for i in range(rules_to_show):
            rule = rules.iloc[i]
            antecedents = ', '.join(rule['antecedents'])
            consequents = ', '.join(rule['consequents'])

            st.caption(f"{i+1}. Jika pelanggan membeli **{antecedents}**, mereka cenderung juga membeli **{consequents}**.")

        st.success(
            "Aturan ini dapat digunakan untuk strategi product bundling dengan menggabungkan barang-barang tersebut dalam "
            "promosi atau paket penjualan. Selain itu, produk ini bisa ditempatkan berdekatan di toko untuk meningkatkan peluang "
            "pembelian impulsif dan memaksimalkan penjualan."
        )



