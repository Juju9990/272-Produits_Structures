import streamlit as st

st.title("📊 Sélection d'un instrument financier")

# Choix du type d'instrument
instrument_type = st.selectbox(
    "Instrument :", ["Option", "Obligation ZC", "Swap", "Autocall Athena"]
)

if instrument_type == "Option":
    option_type = st.selectbox("Type d'option :", ["Call", "Put"])

    if option_type:
        st.subheader(f"Paramètres de l'option {option_type}")
        underlying = st.selectbox(
            "Sous-jacent :", ["S&P 500", "EURO STOXX 50", "Euribor 3M"]
        )
        K = st.number_input("Strike (K)", min_value=0.0, format="%.2f")
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        T = st.number_input("Maturité (en années)", min_value=0.0, format="%.2f")
        quantity = st.number_input("Quantité", min_value=1, step=1)

        st.markdown("### 📋 Résumé de votre saisie")
        st.write(f"Instrument : **Option {option_type}**")
        st.write(f"Sous-jacent : **{underlying}**")
        st.write(f"K = {K}, Nominal = {N}, T = {T} an(s), Quantité = {quantity}")

        if st.button("📊 Calculer le prix de l’option"):
            if K > 0 and T > 0:
                price = K + T  # Prix fictif
                total_price = price * quantity
                st.success(f"💰 Prix unitaire : {price:.2f} €")
                st.info(f"📦 Prix total : {total_price:.2f} €")
            else:
                st.error("Tous les champs doivent être remplis correctement.")

elif instrument_type == "Obligation ZC":
    st.subheader("Paramètres de l'obligation Zéro-Coupon")

    taux_type = st.selectbox("Type de taux :", ["Taux fixe", "Taux variable"])
    if taux_type == "Taux fixe":
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        T = st.number_input("Maturité (en années)", min_value=0.0, format="%.2f")
        taux_coupon = st.number_input(
            "Taux coupon annuel", min_value=0.0, format="%.2f"
        )
        if st.button("📉 Calculer le prix de l'obligation"):
            st.success(f"💰 Prix unitaire : {taux_coupon:.2f} €")
    else:
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        index_ref = st.selectbox("Index de référence :", ["Euribor 3M"])
        st.write("La maturité de l'obligation est de 3 mois.")
        if st.button("📉 Calculer le prix de l'obligation"):
            st.success("💰 Prix unitaire : 100.00 €")
elif instrument_type == "Swap":
    st.markdown("## Généralités")
    N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
    T = st.number_input("Maturité (en années)", min_value=0.0, format="%.2f")
    st.markdown("## Jambe payeuse")
    jambe_payeuse = st.selectbox(
        "Caractéristique de la jambe payeuse:",
        ["Taux payeur fixe", "Taux payeur variable"],
    )

    if jambe_payeuse == "Taux payeur fixe":
        taux_payeur = st.number_input("Taux fixe payeur", min_value=0.0, format="%.2f")
        frequence_payeur = st.selectbox(
            "Fréquence de paiement payeur :", ["Annuel", "Semestriel", "Trimestriel"]
        )
    if jambe_payeuse == "Taux payeur variable":
        taux_payeur = st.selectbox("Index de référence :", ["Euribor 3M"])
        frequence_payeur = st.selectbox(
            "Fréquence de paiement payeur :", ["Annuel", "Semestriel", "Trimestriel"]
        )

    st.markdown("## Jambe receveuse")
    jambe_receveuse = st.selectbox(
        "Caractéristique de la jambe receveuse:",
        ["Taux receveur fixe", "Taux receveur variable"],
    )

    if jambe_receveuse == "Taux receveur fixe":
        taux_receveur = st.number_input(
            "Taux fixe receveur", min_value=0.0, format="%.2f"
        )
        frequence_receveur = st.selectbox(
            "Fréquence de paiement receveur :", ["Annuel", "Semestriel", "Trimestriel"]
        )
    if jambe_receveuse == "Taux receveur variable":
        taux_receveur = st.selectbox("Index de référence :", ["Euribor 3M"])
        frequence_receveur = st.selectbox(
            "Fréquence de paiement receveur:", ["Annuel", "Semestriel", "Trimestriel"]
        )
    if st.button("📈 Calculer le prix du swap"):
        st.success(f"💰 Prix unitaire : 100 €")

if instrument_type == "Autocall Athena":
    # Autocall Athena (Sous-Jacent, Barrière Autocall, Coupon, Maturité, Fixing (Fréquence d'observation)
    st.markdown("## Généralités")
    N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
    T = st.number_input("Maturité (en années)", min_value=0.0, format="%.2f")
    K = st.number_input("Strike (K)", min_value=0.0, format="%.2f")
    coupon = st.number_input("Coupon", min_value=0.0, format="%.2f")
    barriere_autocall = st.number_input(
        "Barrière Autocall", min_value=0.0, format="%.2f"
    )
    fixing = st.selectbox(
        "Fixing (Fréquence d'observation) :", ["Annuel", "Semestriel", "Trimestriel"]
    )
    PDI = st.number_input("PDI", min_value=0.0, format="%.2f")
    # Sous-jacent
    sous_jacent = st.selectbox("Sous-jacent :", ["S&P 500", "EURO STOXX 50"])
    if st.button("📈 Calculer le prix de l'autocall"):
        st.success(f"💰 Prix unitaire : 100 €")
