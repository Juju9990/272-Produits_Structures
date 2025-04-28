import streamlit as st
from fonctionsannexes import *
from maturite import Maturite
from taux import Taux
from smile_volatilite import Volatilite
from produit import Produit
from straddle import Straddle
from call import Call
from put import Put
from call_digit import Call_Digit
from put_digit import Put_Digit
from cap import Cap
from floor import Floor
from tunnel import Tunnel
from obligation import ObligationTxFixe
from obligation_variable import ObligationTxVariable
from obligation_ZC import ObligationZC
from swap import Swap
from autocall import Autocall

st.title("📊 Sélection d'un instrument financier")

# Choix du type d'instrument
instrument_type = st.selectbox(
    "Instrument :",
    [
        "Option",
        "Obligation ZC",
        "Obligation",
        "Swap",
        "Autocall Athena",
        "Option digital",
        "Stratégie",
    ],
)

if instrument_type == "Option":
    #### CALL/PUT & CAP/FLOOR ####
    option_type = st.selectbox("Type d'option :", ["Call", "Put"])
    fixing = None
    if option_type:
        st.subheader(f"Paramètres de l'option {option_type}")
        underlying = st.selectbox("Sous-jacent :", ["Apple", "Euribor 3M"])
        if underlying == "Apple":
            K = st.number_input("Strike (K)", min_value=0.0, format="%.2f", value=200.0)
        elif underlying == "Euribor 3M":
            K = st.number_input("Strike (K)", min_value=0.0, format="%.2f", value=0.03)
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        T = st.number_input(
            "Maturité (en années)", min_value=0, max_value=2, step=1, format="%d"
        )
        quantity = st.number_input("Quantité", min_value=1, step=1)
        fixing = None
        st.markdown("### 📋 Résumé de votre saisie")
        st.write(f"Instrument : **Option {option_type}**")
        st.write(f"Sous-jacent : **{underlying}**")
        st.write(f"K = {K}, Nominal = {N}, T = {T} an(s), Quantité = {quantity}")

        if st.button("📊 Calculer le prix de l’option"):
            mat = Maturite(T, fixing)
            mat.ExpiryDate()
            mat.CreationEcheancier_simulation()
            echeancier_simulation = mat.get_echeancier_simulation()
            mat.CreationEcheancier_fixing()
            echeancier_fixing = mat.get_echeancier_fixing()

            tx = Taux()
            tx.Courbe_TauxZC(echeancier_simulation)
            tx.Courbe_TauxFWD()
            tx.Courbe_TauxFWD_entre_2_simu()
            ZC = tx.get_ZC()
            Fwd = tx.get_Fwd_simu()

            match option_type:
                case "Call":
                    match underlying:
                        case "Apple":
                            V_Call = Volatilite(echeancier_simulation, "call")
                            V_Call.smile()
                            V_Call.smile_Fwd_a_matu()
                            smile_Call = V_Call.get_smile_Fwd_a_matu()

                            mon_call = Call(
                                N,
                                T,
                                fixing,
                                K,
                                underlying,
                                quantity,
                                echeancier_simulation,
                                echeancier_fixing,
                                smile_Call,
                                Fwd,
                                ZC,
                            )
                            mon_call.CoursSpot()
                            mon_call.MonteCarlo()
                            mon_call.Prix()
                            price_call = mon_call.get_price()
                            st.success(
                                f"Le prix de(s) {quantity} {option_type} sur {underlying} : {price_call:.2f} $"
                            )

                        case "Euribor 3M":
                            mon_cap = Cap(
                                N,
                                T,
                                fixing,
                                K,
                                underlying,
                                quantity,
                                echeancier_simulation,
                                echeancier_fixing,
                                Fwd,
                                ZC,
                            )
                            mon_cap.CoursSpot()
                            mon_cap.MonteCarlo()
                            mon_cap.Prix()
                            price_cap = mon_cap.get_price()
                            st.success(
                                f"Le prix de(s) {quantity} {option_type} sur {underlying} : {price_cap:.2f} €"
                            )

                case "Put":
                    match underlying:
                        case "Apple":
                            V_Put = Volatilite(echeancier_simulation, "put")
                            V_Put.smile()
                            V_Put.smile_Fwd_a_matu()
                            smile_Put = V_Put.get_smile_Fwd_a_matu()

                            mon_put = Put(
                                N,
                                T,
                                fixing,
                                K,
                                underlying,
                                quantity,
                                echeancier_simulation,
                                echeancier_fixing,
                                smile_Put,
                                Fwd,
                                ZC,
                            )
                            mon_put.CoursSpot()
                            mon_put.MonteCarlo()
                            mon_put.Prix()
                            price_put = mon_put.get_price()
                            st.success(
                                f"Le prix de(s) {quantity} {option_type} sur {underlying} : {price_put:.2f} $"
                            )

                        case "Euribor 3M":
                            mon_floor = Floor(
                                N,
                                T,
                                fixing,
                                K,
                                underlying,
                                quantity,
                                echeancier_simulation,
                                echeancier_fixing,
                                Fwd,
                                ZC,
                            )
                            mon_floor.CoursSpot()
                            mon_floor.MonteCarlo()
                            mon_floor.Prix()
                            price_floor = mon_floor.get_price()
                            st.success(
                                f"Le prix de(s) {quantity} {option_type} sur {underlying} : {price_floor:.2f} €"
                            )


elif instrument_type == "Obligation ZC":
    #### OBLIGATION ZC ####
    st.subheader("Paramètres de l'obligation Zéro-Coupon")
    fixing = None
    emetteur = st.selectbox("Émetteur :", ["Total", "LVMH", "Airbus"])
    N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
    T = st.number_input("Maturité (en années)", min_value=0, max_value=10, format="%d")
    taux_coupon = st.number_input(
        "Taux coupon ", min_value=0.0, value=0.05, format="%.2f"
    )
    if st.button("📉 Calculer le prix de l'obligation"):
        mat = Maturite(T, fixing)
        mat.ExpiryDate()
        mat.CreationEcheancier_simulation()
        echeancier_simulation = mat.get_echeancier_simulation()
        mat.CreationEcheancier_fixing()
        echeancier_fixing = mat.get_echeancier_fixing()

        match emetteur:
            case "Total":
                spread_de_credit = 0.005

            case "LVMH":
                spread_de_credit = 0.01

            case "Airbus":
                spread_de_credit = 0.03

        taux_facial = taux_coupon + spread_de_credit
        mon_oblig_ZC = ObligationZC(N, T, fixing, taux_facial, echeancier_fixing)
        mon_oblig_ZC.Prix()
        price = mon_oblig_ZC.get_prix()
        price_euro = mon_oblig_ZC.get_prix_euro()
        st.success(
            "Mon Obligation ZC qui verse un taux de {:.2%} (coupon : {:.2%} + spread : {:.2%}) à maturité, vaut {:.2%} du nominal soit {:.2f}€".format(
                mon_oblig_ZC.get_taux_facial(),
                taux_coupon,
                spread_de_credit,
                mon_oblig_ZC.get_prix(),
                mon_oblig_ZC.get_prix_euro(),
            )
        )


elif instrument_type == "Obligation":
    #### OBLIGATION ####
    st.subheader("Paramètres de l'obligation")
    oblig_type = st.selectbox(
        "Type de taux:",
        ["Taux payeur fixe", "Taux payeur variable"],
    )
    emetteur = st.selectbox("Émetteur :", ["Total", "LVMH", "Airbus"])
    N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
    T = st.number_input("Maturité (en années)", min_value=0, max_value=10, format="%d")
    fixing = st.selectbox(
        "Fréquence de paiement :", ["Annuel", "Semestriel", "Trimestriel"]
    )
    if oblig_type == "Taux payeur fixe":
        taux = st.number_input(
            "Taux de coupon par fixing", min_value=0.0, value=0.05, format="%.2f"
        )
    else:
        taux = st.selectbox("Sous-jacent :", ["Euribor 3M"])

    if st.button("📉 Calculer le prix de l'obligation"):
        match oblig_type:
            case "Taux payeur fixe":
                mat = Maturite(T, fixing)
                mat.ExpiryDate()
                mat.CreationEcheancier_simulation()
                echeancier_simulation = mat.get_echeancier_simulation()
                mat.CreationEcheancier_fixing()
                echeancier_fixing = mat.get_echeancier_fixing()

                match emetteur:
                    case "Total":
                        spread_de_credit = 0.005
                    case "LVMH":
                        spread_de_credit = 0.01
                    case "Airbus":
                        spread_de_credit = 0.03

                taux_facial = taux + spread_de_credit
                mon_oblig = ObligationTxFixe(
                    N, T, fixing, taux_facial, echeancier_fixing
                )
                mon_oblig.Prix()
                price = mon_oblig.get_prix()
                price_euro = mon_oblig.get_prix_euro()
                st.success(
                    "Mon Obligation qui verse un taux de {:.2%} (coupon : {:.2%} + spread : {:.2%}) de manière {}le, vaut {:.2%} du nominal soit {:.2f}€".format(
                        mon_oblig.get_taux_facial(),
                        taux,
                        spread_de_credit,
                        mon_oblig.get_fixing(),
                        mon_oblig.get_prix(),
                        mon_oblig.get_prix_euro(),
                    )
                )

            case "Taux payeur variable":
                mat = Maturite(T, fixing)
                mat.ExpiryDate()
                mat.CreationEcheancier_simulation()
                echeancier_simulation = mat.get_echeancier_simulation()
                mat.CreationEcheancier_fixing()
                echeancier_fixing = mat.get_echeancier_fixing()

                tx_oblig = Taux()
                tx_oblig.Courbe_TauxZC_Obligation(echeancier_fixing, fixing)
                ZC_oblig = tx_oblig.get_ZC()
                tx_oblig.Courbe_TauxFWD_entre_2_simu()
                Fwd_oblig = tx_oblig.get_Fwd_simu()

                mon_oblig_variable = ObligationTxVariable(
                    N, T, fixing, echeancier_fixing, Fwd_oblig
                )
                mon_oblig_variable.Prix()
                price = mon_oblig_variable.get_prix()
                price_euro = mon_oblig_variable.get_prix_euro()
                st.success(
                    "Mon Obligation à taux variable qui verse des coupons de manière {}le, vaut {:.2%} du nominal soit {:.2f}€".format(
                        mon_oblig_variable.get_fixing(),
                        mon_oblig_variable.get_prix(),
                        mon_oblig_variable.get_prix_euro(),
                    )
                )


elif instrument_type == "Swap":
    #### SWAP ###
    st.markdown("## Généralités")
    N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
    T = st.number_input("Maturité (en années)", min_value=0, max_value=10, format="%d")

    st.markdown("## Jambe payeuse")
    jambe_payeuse = st.selectbox(
        "Caractéristique de la jambe payeuse:",
        ["Taux payeur fixe", "Taux payeur variable"],
    )
    if jambe_payeuse == "Taux payeur fixe":
        taux_payeur = st.number_input("Taux fixe payeur", min_value=0.0, format="%.2f")

    if jambe_payeuse == "Taux payeur variable":
        taux_payeur = st.selectbox("Index de référence :", ["Euribor 3M"])
        frequence_payeur = st.selectbox(
            "Fréquence de paiement payeur :", ["Annuel", "Semestriel", "Trimestriel"]
        )
        frequence_receveur = frequence_payeur

    st.markdown("## Jambe receveuse")
    if jambe_payeuse == "Taux payeur fixe":
        jambe_receveuse = "Taux receveur variable"
        st.markdown("Caractéristique de la jambe receveuse :")
        st.markdown("Taux receveur taux variable")

        taux_receveur = st.selectbox("Index de référence :", ["Euribor 3M"])
        frequence_receveur = st.selectbox(
            "Fréquence de paiement receveur:", ["Annuel", "Semestriel", "Trimestriel"]
        )
        frequence_payeur = frequence_receveur
    else:
        jambe_receveuse = "Taux receveur fixe"
        st.markdown("Caractéristique de la jambe receveuse :")
        st.markdown("Taux receveur taux fixe")
        taux_receveur = st.number_input(
            "Taux fixe receveur", min_value=0.0, format="%.2f"
        )

    if st.button("📈 Calculer le prix du swap"):
        if jambe_payeuse == "Taux payeur variable":
            fixing = frequence_payeur

            mat = Maturite(T, fixing)
            mat.ExpiryDate()
            mat.CreationEcheancier_simulation()
            echeancier_simulation = mat.get_echeancier_simulation()
            mat.CreationEcheancier_fixing()
            echeancier_fixing = mat.get_echeancier_fixing()

            tx_oblig = Taux()
            tx_oblig.Courbe_TauxZC_Obligation(echeancier_fixing, fixing)
            ZC_oblig = tx_oblig.get_ZC()
            tx_oblig.Courbe_TauxFWD_entre_2_simu()
            Fwd_oblig = tx_oblig.get_Fwd_simu()

            mon_swap = Swap(
                N, T, fixing, taux_receveur, echeancier_fixing, Fwd_oblig, jambe_payeuse
            )
            mon_swap.Prix()
            st.success(
                "Mon swap payeur taux variable vaut {:.2%} du nominal soit {:.2f}€".format(
                    mon_swap.get_prix(), mon_swap.get_prix_euro()
                )
            )

        else:
            fixing = frequence_receveur

            mat = Maturite(T, fixing)
            mat.ExpiryDate()
            mat.CreationEcheancier_simulation()
            echeancier_simulation = mat.get_echeancier_simulation()
            mat.CreationEcheancier_fixing()
            echeancier_fixing = mat.get_echeancier_fixing()

            tx_oblig = Taux()
            tx_oblig.Courbe_TauxZC_Obligation(echeancier_fixing, fixing)
            ZC_oblig = tx_oblig.get_ZC()
            tx_oblig.Courbe_TauxFWD_entre_2_simu()
            Fwd_oblig = tx_oblig.get_Fwd_simu()

            mon_swap = Swap(
                N, T, fixing, taux_payeur, echeancier_fixing, Fwd_oblig, jambe_payeuse
            )
            mon_swap.Prix()
            st.success(
                "Mon swap payeur taux fixe vaut {:.2%} du nominal soit {:.2f}€".format(
                    mon_swap.get_prix(), mon_swap.get_prix_euro()
                )
            )


if instrument_type == "Autocall Athena":
    #### AUTOCALL ATHENA ####
    # Autocall Athena (Sous-Jacent, Barrière Autocall, Coupon, Maturité, Fixing (Fréquence d'observation)
    st.markdown("## Généralités")
    N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
    T = st.number_input("Maturité (en années)", min_value=0, max_value=2, format="%d")
    coupon = st.number_input("Coupon par an", min_value=0.0, format="%.2f")
    barriere_autocall = st.number_input(
        "Barrière Autocall (1=100%)", min_value=0.0, value=1.0, format="%.2f"
    )
    fixing = st.selectbox(
        "Fixing (Fréquence d'observation) :", ["Annuel", "Semestriel", "Trimestriel"]
    )
    risque_capital = st.selectbox("Risque en capital : ", ["Oui", "Non"])
    if risque_capital == "Oui":
        PDI_Strike = st.number_input(
            "Strike du PDI (1=100%)", min_value=0.0, value=1.0, format="%.2f"
        )
        PDI_barriere = st.number_input(
            "Barrière du PDI", min_value=0.0, value=0.3, format="%.2f"
        )
    else:
        PDI_Strike = 0
        PDI_barriere = 0
    # Sous-jacent
    underlying = st.selectbox("Sous-jacent :", ["Apple"])
    if st.button("📈 Calculer le prix de l'autocall"):
        mat = Maturite(T, fixing)
        mat.ExpiryDate()
        mat.CreationEcheancier_simulation()
        echeancier_simulation = mat.get_echeancier_simulation()
        mat.CreationEcheancier_fixing()
        echeancier_fixing = mat.get_echeancier_fixing()

        tx = Taux()
        tx.Courbe_TauxZC(echeancier_simulation)
        tx.Courbe_TauxFWD()
        tx.Courbe_TauxFWD_entre_2_simu()
        ZC = tx.get_ZC()
        Fwd = tx.get_Fwd_simu()

        mon_autocall = Autocall(
            N,
            T,
            fixing,
            underlying,
            echeancier_fixing,
            echeancier_simulation,
            coupon,
            barriere_autocall,
            PDI_Strike,
            PDI_barriere,
            ZC,
        )
        mon_autocall.Calibration_Heston()
        calib = mon_autocall.get_calibration()

        mon_autocall.CoursSpot()
        mon_autocall.MonteCarlo()
        prix = mon_autocall.get_prix()
        prix_dollar = mon_autocall.get_prix_dollar()
        st.success(
            "Mon Autocall sur {} avec une barrière autocall de {:.2f}, PDI (K={:.2%}, B={:.2%}) et un coupon par an de {:.2%} vaut {:.2%} soit {:.2f}$".format(
                underlying,
                barriere_autocall,
                PDI_Strike,
                PDI_barriere,
                coupon,
                prix,
                prix_dollar,
            )
        )


if instrument_type == "Option digital":
    option_digital = st.selectbox(
        "Type d'option digital :", ["Call digital", "Put digital"]
    )
    fixing = None
    if option_digital:
        st.subheader(f"Paramètres de l'option {option_digital}")
        K = st.number_input("Strike (K)", min_value=0.0, value=200.0, format="%.2f")
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        # start_date = st.date_input("Date de début")
        T = st.number_input(
            "Maturité (en années)", min_value=0, max_value=2, format="%d"
        )
        sous_jacent = st.selectbox("Sous-jacent :", ["Apple"])
        quantity = st.number_input("Quantité", min_value=1, step=1)
        coupon = st.number_input("Coupon", min_value=0.0, format="%.2f")
    if st.button("📈 Calculer le prix de la digit"):
        mat = Maturite(T, fixing)
        mat.ExpiryDate()
        mat.CreationEcheancier_simulation()
        echeancier_simulation = mat.get_echeancier_simulation()
        mat.CreationEcheancier_fixing()
        echeancier_fixing = mat.get_echeancier_fixing()

        tx = Taux()
        tx.Courbe_TauxZC(echeancier_simulation)
        tx.Courbe_TauxFWD()
        tx.Courbe_TauxFWD_entre_2_simu()
        ZC = tx.get_ZC()
        Fwd = tx.get_Fwd_simu()
        if option_digital == "Call digital":
            V_Call = Volatilite(echeancier_simulation, "call")
            V_Call.smile()
            V_Call.smile_Fwd_a_matu()
            smile_Call = V_Call.get_smile_Fwd_a_matu()

            mon_call_digit = Call_Digit(
                N,
                T,
                fixing,
                K,
                sous_jacent,
                quantity,
                coupon,
                echeancier_simulation,
                echeancier_fixing,
                smile_Call,
                Fwd,
                ZC,
            )
            mon_call_digit.CoursSpot()
            mon_call_digit.MonteCarlo()
            mon_call_digit.Prix()
            price_call_digit = mon_call_digit.get_price()
            st.success(
                "Le prix de(s) {:.0f} Call Digit sur {} de strike {:.2f}\\$ est de {:.2f}\\$".format(
                    mon_call_digit.get_quantity(),
                    mon_call_digit.get_sous_jacent(),
                    mon_call_digit.get_strike(),
                    price_call_digit,
                )
            )

        else:
            V_Put = Volatilite(echeancier_simulation, "put")
            V_Put.smile()
            V_Put.smile_Fwd_a_matu()
            smile_Put = V_Put.get_smile_Fwd_a_matu()

            mon_put_digit = Put_Digit(
                N,
                T,
                fixing,
                K,
                sous_jacent,
                quantity,
                coupon,
                echeancier_simulation,
                echeancier_fixing,
                smile_Put,
                Fwd,
                ZC,
            )
            mon_put_digit.CoursSpot()
            mon_put_digit.MonteCarlo()
            mon_put_digit.Prix()
            price_put_digit = mon_put_digit.get_price()
            st.success(
                "Le prix de(s) {:.0f} put Digit sur {} de strike {:.2f}\\$ est de {:.2f}\\$".format(
                    mon_put_digit.get_quantity(),
                    mon_put_digit.get_sous_jacent(),
                    mon_put_digit.get_strike(),
                    price_put_digit,
                )
            )


if instrument_type == "Stratégie":
    instrument_type_bis = st.selectbox(
        "Stratégie :", ["Obligation convertible", "Tunnel", "Straddle"]
    )
    if instrument_type_bis == "Obligation convertible":
        st.markdown("## Partie obligataire")
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        T = st.number_input("Maturité (en années)", min_value=0.0, format="%.2f")
        coupon = st.number_input("Coupon", min_value=0.0, format="%.2f")
        fixing = st.selectbox(
            "Fréquence de paiement :", ["Annuel", "Semestriel", "Trimestriel"]
        )
        st.markdown("## Partie optionnelle")
        fixing = None
        K = st.number_input("Strike (K)", min_value=0.0, format="%.2f")
        underlying = st.selectbox("Sous-jacent :", ["Apple"])
        conversion_ratio = st.number_input(
            "Ratio de conversion", min_value=0.0, format="%.2f"
        )
        if st.button("📈 Calculer le prix de l'obligation convertible"):
            mat = Maturite(T, fixing)
            mat.ExpiryDate()
            mat.CreationEcheancier_simulation()
            echeancier_simulation = mat.get_echeancier_simulation()
            mat.CreationEcheancier_fixing()
            echeancier_fixing = mat.get_echeancier_fixing()

            tx = Taux()
            tx.Courbe_TauxZC(echeancier_simulation)
            tx.Courbe_TauxFWD()
            tx.Courbe_TauxFWD_entre_2_simu()
            ZC = tx.get_ZC()
            Fwd = tx.get_Fwd_simu()

            mon_oblig = ObligationTxFixe(N, T, fixing, coupon, echeancier_fixing)
            mon_oblig.Prix()
            price_euro = mon_oblig.get_prix_euro()

            V_Call = Volatilite(echeancier_simulation, "call")
            V_Call.smile()
            V_Call.smile_Fwd_a_matu()
            smile_Call = V_Call.get_smile_Fwd_a_matu()

            mon_call = Call(
                N,
                T,
                fixing,
                K,
                underlying,
                1,
                echeancier_simulation,
                echeancier_fixing,
                smile_Call,
                Fwd,
                ZC,
            )
            mon_call.CoursSpot()
            mon_call.MonteCarlo()
            mon_call.Prix()
            price_call = mon_call.get_price()

            price_strat = price_euro + price_call
            st.success(
                "Le prix de l'obligation convertible est de {:.2f}€".format(price_strat)
            )

    if instrument_type_bis == "Tunnel":
        st.markdown("## Généralités")
        fixing = None
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        T = st.number_input(
            "Maturité (en années)", min_value=0, max_value=2, format="%d"
        )
        sous_jacent = st.selectbox("Sous-jacent :", ["Euribor 3M"])
        st.markdown("## Partie Call")
        K1 = st.number_input("Strike 1 (K1)", min_value=0.0, value=0.03, format="%.2f")
        st.markdown("## Partie Put")
        K2 = st.number_input("Strike 2 (K2)", min_value=0.0, value=0.01, format="%.2f")
        if st.button("📈 Calcul"):
            mat = Maturite(T, fixing)
            mat.ExpiryDate()
            mat.CreationEcheancier_simulation()
            echeancier_simulation = mat.get_echeancier_simulation()
            mat.CreationEcheancier_fixing()
            echeancier_fixing = mat.get_echeancier_fixing()

            tx = Taux()
            tx.Courbe_TauxZC(echeancier_simulation)
            tx.Courbe_TauxFWD()
            tx.Courbe_TauxFWD_entre_2_simu()
            ZC = tx.get_ZC()
            Fwd = tx.get_Fwd_simu()

            mon_tunnel = Tunnel(
                N,
                T,
                fixing,
                K2,
                K1,
                sous_jacent,
                echeancier_simulation,
                echeancier_fixing,
                Fwd,
                ZC,
            )
            mon_tunnel.Prix()
            price_cap = mon_tunnel.get_price_cap()
            price_floor = mon_tunnel.get_price_floor()
            price_strat = mon_tunnel.get_price_strat()
            st.success(
                "Le prix du Cap sur {} de strike {:.2f} est de {:.2f}€".format(
                    mon_tunnel.get_sous_jacent(), mon_tunnel.get_strike_cap(), price_cap
                )
            )
            st.success(
                "Le prix du Floor sur {} de strike {:.2f} est de {:.2f}€".format(
                    mon_tunnel.get_sous_jacent(),
                    mon_tunnel.get_strike_floor(),
                    price_floor,
                )
            )
            st.success(
                "Le prix du Tunnel [Floor {:.2f}, Cap {:.2f}] sur {} est de {:.2f}€".format(
                    mon_tunnel.get_strike_floor(),
                    mon_tunnel.get_strike_cap(),
                    mon_tunnel.get_sous_jacent(),
                    price_strat,
                )
            )

    if instrument_type_bis == "Straddle":
        st.markdown("## Généralités")
        fixing = None
        N = st.number_input("Nominal (N)", min_value=0.0, format="%.2f")
        T = st.number_input(
            "Maturité (en années)", min_value=0, max_value=2, format="%d"
        )
        sous_jacent = st.selectbox("Sous-jacent :", ["Apple"])
        if st.button("📈 Calcul"):
            mat = Maturite(T, fixing)
            mat.ExpiryDate()
            mat.CreationEcheancier_simulation()
            echeancier_simulation = mat.get_echeancier_simulation()
            mat.CreationEcheancier_fixing()
            echeancier_fixing = mat.get_echeancier_fixing()

            tx = Taux()
            tx.Courbe_TauxZC(echeancier_simulation)
            tx.Courbe_TauxFWD()
            tx.Courbe_TauxFWD_entre_2_simu()
            ZC = tx.get_ZC()
            Fwd = tx.get_Fwd_simu()

            V_Call = Volatilite(echeancier_simulation, "call")
            V_Call.smile()
            V_Call.smile_Fwd_a_matu()
            smile_Call = V_Call.get_smile_Fwd_a_matu()

            V_Put = Volatilite(echeancier_simulation, "put")
            V_Put.smile()
            V_Put.smile_Fwd_a_matu()
            smile_Put = V_Put.get_smile_Fwd_a_matu()

            mon_straddle = Straddle(
                N,
                T,
                fixing,
                sous_jacent,
                echeancier_simulation,
                echeancier_fixing,
                smile_Call,
                smile_Put,
                Fwd,
                ZC,
            )
            mon_straddle.Prix()
            price_call = mon_straddle.get_price_call()
            price_put = mon_straddle.get_price_put()
            price_strat = mon_straddle.get_price_strat()
            st.success(
                "Le prix du Call ATM sur {} est égal à {:.2f}$".format(
                    mon_straddle.get_sous_jacent(), price_call
                )
            )
            st.success(
                "Le prix du Put ATM sur {} est égal à {:.2f}$".format(
                    mon_straddle.get_sous_jacent(), price_put
                )
            )
            st.success(
                "Le prix du Straddle sur {} est de {:.2f}$".format(
                    mon_straddle.get_sous_jacent(), price_strat
                )
            )
