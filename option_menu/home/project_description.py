import streamlit as st

def project_description():
    cols = st.columns(2)
    with cols[0]:
        st.header("HOME")
        st.markdown("**Selamat datang di Sakinah Mart Analytics!**")
        st.markdown("Proyek ini menghadirkan visualisasi dan analisis mendalam dari data penjualan Sakinah Mart sepanjang tahun 2023.")
        st.markdown(
                        """
                        <a href="https://sakinahmart.com/" target="_blank">
                            <button style="background-color:#009b4c; color:white; border:none; padding:10px 25px; text-align:center; text-decoration:none; font-size:14px; border-radius:20px; cursor:pointer;">
                                Sakinah Mart Website
                            </button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
        
    with cols[1]:
        try:
            st.image("sakinah-mart.png", use_container_width=True)
        except TypeError:
            st.image("sakinah-mart.png", use_column_width=True)

    st.markdown("""<div style="text-align: justify;">
    Sakinah Mart adalah ritel modern berbasis syariah dengan 20 cabang di Jawa Timur, 
    yang bertujuan memberikan manfaat bagi masyarakat melalui produk berkualitas dengan harga terjangkau. 
    Namun, data transaksi yang melimpah seperti waktu pembelian, produk yang dibeli, dan frekuensi pembelian belum diolah secara optimal, 
    sehingga berisiko menimbulkan waste of inventory.
    Untuk mengatasi hal ini dan tetap bersaing di pasar, project kali ini menggunakan algoritma Apriori untuk mengidentifikasi pola pembelian konsumen, seperti product bundling dan penataan letak barang, 
    serta metode Vector Autoregressive (VAR) untuk memprediksi kebutuhan pelanggan dan mengelola persediaan secara efisien. Kombinasi kedua metode ini diharapkan dapat mengoptimalkan strategi penjualan, meningkatkan efisiensi operasional, dan menjaga kepuasan pelanggan.
    </div>""", unsafe_allow_html=True)