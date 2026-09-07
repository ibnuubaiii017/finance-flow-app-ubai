import streamlit as st
import datetime
import pandas as pd
from database import init_db, add_transaction, update_transaction, delete_transaction, get_all_transactions
from parser import parse_receipt_image, parse_quick_text

init_db()

# Setup Halaman
st.set_page_config(page_title="FinanceFlow", page_icon="💳", layout="centered")

# CSS Styling untuk UI Modern & Terang
st.markdown("""
    <style>
    /* Card Saldo Utama */
    .card-saldo {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 22px;
        border-radius: 18px;
        margin-bottom: 16px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15);
    }
    
    /* Card Warning Pengeluaran Terbesar */
    .card-top-expense {
        background-color: #fff1f2;
        border-left: 5px solid #f43f5e;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    /* Item List Transaksi */
    .tx-row {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# DITAMBAHKAN ROKO & ICE KRIM
CATEGORIES_EXPENSE = [
    "🍔 Makanan", 
    "🚬 Rokok", 
    "🍦 Ice / Es Krim", 
    "🚗 Transport", 
    "🛍️ Belanja", 
    "💡 Tagihan", 
    "🎬 Hiburan", 
    "📦 Lainnya"
]
CATEGORIES_INCOME = ["💼 Gaji", "🎁 Bonus", "📈 Investasi", "🏷️ Penjualan", "📦 Lainnya"]

# TAB UTAMA
tab_dash, tab_input = st.tabs(["📊 Dashboard & Analytics", "➕ Tambah Transaksi"])

# ==========================================
# TAB 1: DASHBOARD & ANALYTICS
# ==========================================
with tab_dash:
    st.title("💳 FinanceFlow")
    
    # Filter Bulan
    selected_month = st.selectbox("Pilih Bulan", range(1, 13), index=datetime.date.today().month - 1)
    
    raw_data = get_all_transactions()
    
    if raw_data:
        df = pd.DataFrame(raw_data, columns=["ID", "Tipe", "Nominal", "Kategori", "Keterangan", "Tanggal", "Metode"])
        df['Tanggal_DT'] = pd.to_datetime(df['Tanggal'])
        
        current_year = datetime.date.today().year
        df_filtered = df[(df['Tanggal_DT'].dt.month == selected_month) & (df['Tanggal_DT'].dt.year == current_year)]
        
        total_income = df_filtered[df_filtered['Tipe'] == 'Income']['Nominal'].sum()
        total_expense = df_filtered[df_filtered['Tipe'] == 'Expense']['Nominal'].sum()
        balance = total_income - total_expense

        # 1. CARD SALDO UTAMA
        st.markdown(f"""
            <div class="card-saldo">
                <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 700; letter-spacing: 0.5px;">SISA SALDO BULAN INI</div>
                <div style="font-size: 2.3rem; font-weight: 800; margin: 6px 0;">Rp {balance:,.0f}</div>
                <hr style="border-color: #334155; margin: 14px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <span style="color: #34d399; font-size: 0.85rem;">↓ Pemasukan</span><br>
                        <b style="font-size: 1.15rem; color: #34d399;">Rp {total_income:,.0f}</b>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #f87171; font-size: 0.85rem;">↑ Pengeluaran</span><br>
                        <b style="font-size: 1.15rem; color: #f87171;">Rp {total_expense:,.0f}</b>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. CARD PENGELUARAN TERBESAR (DETEKSI PALING BOROS)
        df_exp = df_filtered[df_filtered['Tipe'] == 'Expense']
        if not df_exp.empty and total_expense > 0:
            cat_group = df_exp.groupby("Kategori")["Nominal"].sum().reset_index()
            top_category = cat_group.sort_values(by="Nominal", ascending=False).iloc[0]
            
            top_cat_name = top_category["Kategori"]
            top_cat_amount = top_category["Nominal"]
            top_percentage = (top_cat_amount / total_expense) * 100

            st.markdown(f"""
                <div class="card-top-expense">
                    <div style="font-size: 0.78rem; color: #e11d48; font-weight: 700; text-transform: uppercase;">🔥 Kategori Paling Boros Bulan Ini</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                        <span style="font-size: 1.2rem; font-weight: 800; color: #881337;">{top_cat_name}</span>
                        <span style="font-size: 1.15rem; font-weight: 800; color: #e11d48;">Rp {top_cat_amount:,.0f} ({top_percentage:.1f}%)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 3. REKAP TOTAL BELANJA PER KATEGORI
            with st.expander("📊 Rekap Pengeluaran per Kategori", expanded=False):
                for _, c_row in cat_group.sort_values(by="Nominal", ascending=False).iterrows():
                    c_pct = (c_row["Nominal"] / total_expense) * 100
                    st.write(f"**{c_row['Kategori']}**")
                    st.progress(c_pct / 100)
                    st.caption(f"Total: Rp {c_row['Nominal']:,.0f} ({c_pct:.1f}% dari total pengeluaran)")
                    st.divider()

        # 4. RIWAYAT TRANSAKSI
        st.subheader("📝 Riwayat Transaksi")
        
        if not df_filtered.empty:
            for _, row in df_filtered.iterrows():
                is_exp = row['Tipe'] == 'Expense'
                color = "#ef4444" if is_exp else "#10b981"
                sign = "-" if is_exp else "+"
                
                col_txt, col_pop = st.columns([3, 1])
                with col_txt:
                    st.markdown(f"""
                        <div class="tx-row">
                            <div style="font-weight: 700; color: #0f172a; font-size: 1rem;">{row['Keterangan'] if row['Keterangan'] else row['Kategori']}</div>
                            <div style="font-size: 0.8rem; color: #64748b;">{row['Tanggal']} • {row['Kategori']}</div>
                            <div style="font-weight: 800; color: {color}; font-size: 1.1rem; margin-top: 4px;">{sign}Rp {row['Nominal']:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col_pop:
                    with st.popover("⚙️ Edit"):
                        st.caption(f"Edit Transaksi ID #{row['ID']}")
                        e_type = st.radio("Tipe", ["Expense", "Income"], index=0 if is_exp else 1, key=f"t_{row['ID']}")
                        e_amount = st.number_input("Nominal (Rp)", value=float(row['Nominal']), key=f"a_{row['ID']}")
                        e_merchant = st.text_input("Keterangan", value=row['Keterangan'], key=f"m_{row['ID']}")
                        
                        cats = CATEGORIES_EXPENSE if e_type == "Expense" else CATEGORIES_INCOME
                        idx = cats.index(row['Kategori']) if row['Kategori'] in cats else 0
                        e_cat = st.selectbox("Kategori", cats, index=idx, key=f"c_{row['ID']}")
                        
                        if st.button("Simpan Perubahan", key=f"save_{row['ID']}"):
                            update_transaction(row['ID'], e_type, e_amount, e_cat, e_merchant, row['Tanggal'])
                            st.success("Tersimpan!")
                            st.rerun()
                            
                        if st.button("Hapus Transaksi", key=f"del_{row['ID']}", type="primary"):
                            delete_transaction(row['ID'])
                            st.success("Dihapus!")
                            st.rerun()
        else:
            st.info("Belum ada transaksi di bulan ini.")
    else:
        st.info("Belum ada data transaksi. Silakan tambah di tab sebelah!")

# ==========================================
# TAB 2: TAMBAH TRANSAKSI
# ==========================================
with tab_input:
    st.subheader("➕ Tambah Transaksi")
    
    input_method = st.radio("Metode Input:", ["📝 Manual", "⚡ Quick Text", "📷 Scan Struk"], horizontal=True)
    st.divider()

    # 1. MANUAL
    if input_method == "📝 Manual":
        tx_type = st.radio("Tipe Transaksi", ["Expense", "Income"], horizontal=True)
        amount = st.number_input("Nominal (Rp)", min_value=0.0, step=5000.0)
        
        cats = CATEGORIES_EXPENSE if tx_type == "Expense" else CATEGORIES_INCOME
        category = st.selectbox("Kategori", cats)
        merchant = st.text_input("Keterangan / Merchant", placeholder="misal: Sampoerna / Mixue / Gaji")
        date = st.date_input("Tanggal", datetime.date.today())
        
        if st.button("💾 Simpan Transaksi", type="primary", use_container_width=True):
            if amount > 0:
                add_transaction(tx_type, amount, category, merchant, str(date), "manual")
                st.success("Berhasil disimpan!")
                st.rerun()
            else:
                st.error("Nominal harus diisi!")

    # 2. QUICK TEXT
    elif input_method == "⚡ Quick Text":
        st.caption("Contoh: `Rokok 30rb` atau `Mixue 15k` atau `Gaji 5000000`")
        q_type = st.radio("Tipe Transaksi", ["Expense", "Income"], horizontal=True, key="qt_mode")
        q_text = st.text_input("Ketik Kalimat Cepat:")
        
        if st.button("⚡ Simpan Cepat", type="primary", use_container_width=True):
            if q_text:
                parsed = parse_quick_text(q_text)
                add_transaction(q_type, parsed['amount'], "📦 Lainnya", parsed['merchant'], str(datetime.date.today()), "quick_text")
                st.success("Berhasil disimpan!")
                st.rerun()

    # 3. OCR STRUK
    elif input_method == "📷 Scan Struk":
        up_file = st.file_uploader("Upload Foto Struk", type=["jpg", "jpeg", "png"])
        if up_file and st.button("🔍 Scan Sekarang"):
            st.session_state['ocr_data'] = parse_receipt_image(up_file)
            
        if 'ocr_data' in st.session_state:
            res = st.session_state['ocr_data']
            with st.form("ocr_form_clean"):
                o_amount = st.number_input("Nominal Struk", value=res['amount'])
                o_merchant = st.text_input("Nama Merchant", value="")
                o_cat = st.selectbox("Kategori", CATEGORIES_EXPENSE)
                o_date = st.date_input("Tanggal", datetime.date.today())
                
                if st.form_submit_button("💾 Konfirmasi & Simpan"):
                    add_transaction("Expense", o_amount, o_cat, o_merchant, str(o_date), "ocr")
                    del st.session_state['ocr_data']
                    st.success("Berhasil disimpan!")
                    st.rerun()