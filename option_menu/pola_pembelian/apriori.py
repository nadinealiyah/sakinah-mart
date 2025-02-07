import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.cm as cm
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
    st.markdown(
        "<div style='font-weight: bold; font-size: 18px;'>Hasil Rules Items</div>",
        unsafe_allow_html=True
    )
    # Apriori
    frequent_itemsets = apriori(basket_sets, min_support=0.0001, use_colnames=True, low_memory=True)

    # Association rules - using lift
    rules = association_rules(frequent_itemsets, num_itemsets=len(frequent_itemsets))

    # Customizable function to change the lift and confidence
    def rules_mod(lift, confidence):
        '''rules_mod is a function to control the rules 
        based on lift and confidence threshold'''
        filtered_rules = rules[(rules['lift'] >= lift) & (rules['confidence'] >= confidence)]
        return filtered_rules.reset_index(drop=True)  # Reset index to start from 0

    return rules_mod(1, 1)

def apriori_visual(rules):
    with st.expander("Visualisasi"):
        rules_to_show = st.slider(
            'Jumlah rules untuk divisualisasikan',
            min_value=1,
            max_value=len(rules),
            value=5,
            step=1,
        )

        # Mengurutkan rules berdasarkan lift dari yang terbesar ke terkecil
        sorted_rules = rules.sort_values(by="lift", ascending=False).head(rules_to_show)

        # Menggabungkan antecedents dan consequents sebagai label
        labels = [
            f"{', '.join(antecedents)} → {', '.join(consequents)}"
            for antecedents, consequents in zip(sorted_rules['antecedents'], sorted_rules['consequents'])
        ]
        
        lift_values = sorted_rules['lift'].values

        fig, ax = plt.subplots(figsize=(10, 6))
        y_pos = np.arange(len(labels))


        ax.barh(y_pos, lift_values, color='#abce19')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel("Lift Value")
        ax.set_title("Bar Chart of Apriori Rules")

        plt.gca().set_facecolor("#F0F2F6")  # Warna latar belakang area grafik
        plt.gcf().patch.set_facecolor("#F0F2F6") 
        plt.gca().invert_yaxis()  # Membalik sumbu y agar aturan dengan lift tertinggi ada di atas
        st.pyplot(fig)

def analyze_rules(rules):
    best_rule = rules.iloc[rules['lift'].idxmax()]
    best_rule_text = (
        f"Jika pelanggan membeli **{', '.join(best_rule['antecedents'])}**, mereka cenderung juga membeli "
        f"**{', '.join(best_rule['consequents'])}**)."
    )

    kesimpulan = (
        f"Aturan ini dapat digunakan untuk strategi product bundling dengan menggabungkan barang-barang tersebut dalam "
        f"promosi atau paket penjualan. Selain itu, produk ini bisa ditempatkan berdekatan di toko untuk meningkatkan peluang "
        f"pembelian impulsif dan memaksimalkan penjualan."
    )

    st.success(f"**Kesimpulan:** {best_rule_text}\n\n**Rekomendasi:** {kesimpulan}")

