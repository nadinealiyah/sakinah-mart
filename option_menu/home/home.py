import streamlit as st

def project_description():
    cols = st.columns(2)
    with cols[0]:
        st.header("HOME")
        st.markdown("**Selamat datang di Sakinah Mart Analytics!**")
        st.markdown("Proyek ini menghadirkan visualisasi dan analisis mendalam dari data penjualan Sakinah Mart.")
        st.markdown(
                        """
                        <a href="https://sakinahmart.com/" target="_blank">
                            <button style="background-color:#05AF58; color:white; border:none; padding:10px 25px; text-align:center; text-decoration:none; font-size:14px; border-radius:20px; cursor:pointer;">
                               Sakinah Mart Website
                            </button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
        st.write("  ")

    with cols[1]:
        try:
            st.image("sakinah-mart.png", use_container_width=True)
        except TypeError:
            st.image("sakinah-mart.png", use_column_width=True)

    st.markdown("""<div style="text-align: justify;">
    Sakinah Mart adalah ritel modern berbasis syariah di Jawa Timur, 
    yang bertujuan memberikan manfaat bagi masyarakat melalui produk berkualitas dengan harga terjangkau. 
    Untuk mengatasi hal ini dan tetap bersaing di pasar, project kali ini menggunakan algoritma Apriori untuk mengidentifikasi pola pembelian konsumen, dengan bertujuan untuk product bundling dan penataan letak barang.
    Serta metode Recurrent Neural Network (RNN) untuk memprediksi penjualan barang sehingga dapat mengelola persediaan secara efisien. 
    Kombinasi kedua metode ini diharapkan dapat mengoptimalkan strategi penjualan, meningkatkan efisiensi operasional, dan menjaga kepuasan pelanggan.
    </div>""", unsafe_allow_html=True)