from fonctionsannexes import *
from maturite import Maturite
from taux import Taux
from smile_volatilite import Volatilite
from produit import Produit
from straddle import Straddle
from call import Call
from put import Put
from cap import Cap
from floor import Floor
from tunnel import Tunnel
from obligation import ObligationTxFixe
from obligation_variable import ObligationTxVariable
from obligation_ZC import ObligationZC
from swap import Swap
from autocall import Autocall

# generer_smile("Apple")
# print("Done")

mat = Maturite(5, "Trimestriel")
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

"""
V_Call = Volatilite(echeancier_simulation, "call")
V_Call.smile()
V_Call.smile_Fwd_a_matu()
smile_Call = V_Call.get_smile_Fwd_a_matu()

V_Put = Volatilite(echeancier_simulation, "put")
V_Put.smile()
V_Put.smile_Fwd_a_matu()
smile_Put = V_Put.get_smile_Fwd_a_matu()

mon_call = Call(
    100000,
    1,
    None,
    250,
    "Apple",
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

mon_put = Put(
    100000,
    1,
    None,
    250,
    "Apple",
    1,
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
print(
    "Le prix des {:.2f} Call sur {} de strike {:.2f}$ est de {:.2f}$".format(
        mon_call.get_quantity(),
        mon_call.get_sous_jacent(),
        mon_call.get_strike(),
        price_call,
    )
)
print(
    "Le prix des {:.2f} Put sur {} de strike {:.2f}$ est de {:.2f}$".format(
        mon_put.get_quantity(),
        mon_put.get_sous_jacent(),
        mon_put.get_strike(),
        price_put,
    )
)

#####  STRADDLE  ####
mon_straddle = Straddle(100000, 2, None, "Apple", echeancier_simulation, echeancier_fixing, smile_Call, smile_Put, Fwd, ZC)
mon_straddle.Prix()
price_call = mon_straddle.get_price_call()
price_put = mon_straddle.get_price_put()
price_strat = mon_straddle.get_price_strat()
print("Le prix du Call ATM sur {} est égal à {:.2f}$".format(mon_straddle.get_sous_jacent(), price_call))
print("Le prix du Put ATM sur {} est égal à {:.2f}$".format(mon_straddle.get_sous_jacent(), price_put))
print("Le prix du Straddle sur {} est égal à {:.2f}$".format(mon_straddle.get_sous_jacent(), price_strat))

#####  CAP  ####
mon_cap = Cap(100000, 2, None, 0.05, "Euribor 3M", 1, echeancier_simulation, echeancier_fixing, Fwd, ZC)
mon_cap.CoursSpot()
mon_cap.MonteCarlo()
mon_cap.Prix()
price_cap = mon_cap.get_price()
print("Le prix des {:.2f} Cap sur {} de strike {:.2f}, pour un nominal de {:.2f}€ est de {:.2f}€".format(mon_cap.get_quantity(), mon_cap.get_sous_jacent(), mon_cap.get_strike(), mon_cap.get_nominal() , price_cap))

#####  FLOOR  ####
mon_floor = Floor(100000, 2, None, 0.05, "Euribor 3M", 1, echeancier_simulation, echeancier_fixing, Fwd, ZC)
mon_floor.CoursSpot()
mon_floor.MonteCarlo()
mon_floor.Prix()
price_floor = mon_floor.get_price()
print("Le prix des {:.2f} Floor sur {} de strike {:.2f}, pour un nominal de {:.2f}€ est de {:.2f}€".format(mon_floor.get_quantity(), mon_floor.get_sous_jacent(), mon_floor.get_strike(), mon_floor.get_nominal() , price_floor))

#####  TUNNEL  ####
mon_tunnel = Tunnel(100000, 2, None, 0.01, 0.03, "Euribor 3M", echeancier_simulation, echeancier_fixing, Fwd, ZC)
mon_tunnel.Prix()
price_cap = mon_tunnel.get_price_cap()
price_floor = mon_tunnel.get_price_floor()
price_strat = mon_tunnel.get_price_strat()
print("Le prix du Cap sur {} de strike {:.2f} est de {:.2f}€".format(mon_tunnel.get_sous_jacent(), mon_tunnel.get_strike_cap(), price_cap))
print("Le prix du Floor sur {} de strike {:.2f} est de {:.2f}€".format(mon_tunnel.get_sous_jacent(), mon_tunnel.get_strike_floor(), price_floor))
print("Le prix du Tunnel [Floor {:.2f}, Cap {:.2f}] sur {} est de {:.2f}€".format(mon_tunnel.get_strike_floor(), mon_tunnel.get_strike_cap(), mon_tunnel.get_sous_jacent(), price_strat))

#####  OBLIGATION TAUX FIXE  ####
mon_oblig = ObligationTxFixe(100000, 2, "Trimestriel", 0.02, echeancier_fixing)
mon_oblig.Prix()
price = mon_oblig.get_prix()
price_euro = mon_oblig.get_prix_euro()
print("Mon Obligation qui verse un taux de {:.2%} de manière {}, vaut {:.2%} du nominal soit {:.2f}€".format(mon_oblig.get_taux_facial(), mon_oblig.get_fixing(), mon_oblig.get_prix(), mon_oblig.get_prix_euro()))

#####  OBLIGATION TAUX VARIABLE  ####
tx_oblig = Taux()
tx_oblig.Courbe_TauxZC_Obligation(echeancier_fixing, "Trimestriel")
ZC_oblig = tx_oblig.get_ZC()
tx_oblig.Courbe_TauxFWD_entre_2_simu()
Fwd_oblig = tx_oblig.get_Fwd_simu()

mon_oblig_variable = ObligationTxVariable(
    100000, 2, "Trimestriel", echeancier_fixing, Fwd_oblig
)
mon_oblig_variable.Prix()
price = mon_oblig_variable.get_prix()
price_euro = mon_oblig_variable.get_prix_euro()

print(
    "Mon Obligation à taux variable qui verse des coupons de manière {}, vaut {:.2%} du nominal soit {:.2f}€".format(
        mon_oblig_variable.get_fixing(),
        mon_oblig_variable.get_prix(),
        mon_oblig_variable.get_prix_euro(),
    )
)

#####  OBLIGATION ZÉRO COUPON  ####
mon_oblig_ZC = ObligationZC(100000, 2, None, 0.02, echeancier_fixing)
mon_oblig_ZC.Prix()
price = mon_oblig_ZC.get_prix()
price_euro = mon_oblig_ZC.get_prix_euro()
print("Mon Obligation ZC qui verse un taux de {:.2%} à maturité, vaut {:.2%} du nominal soit {:.2f}€".format(mon_oblig_ZC.get_taux_facial(), mon_oblig_ZC.get_prix(), mon_oblig_ZC.get_prix_euro()))
"""
####  SWAP  ####
tx_oblig = Taux()
tx_oblig.Courbe_TauxZC_Obligation(echeancier_fixing, "Trimestriel")
ZC_oblig = tx_oblig.get_ZC()
tx_oblig.Courbe_TauxFWD_entre_2_simu()
Fwd_oblig = tx_oblig.get_Fwd_simu()

mon_swap = Swap(
    100000, 2, "Trimestriel", 0.02, echeancier_fixing, Fwd_oblig, "Taux payeur variable"
)
mon_swap.Prix()
print(
    "Mon swap payeur taux variable vaut {:.2%} du nominal soit {:.2f}€".format(
        mon_swap.get_prix(), mon_swap.get_prix_euro()
    )
)

# #####  AUTOCALL ATHENA  ####
# mon_autocall = Autocall(100000, 2, "Trimestriel", "Apple", echeancier_fixing, echeancier_simulation, 0.15, 1, 1, 0.3, ZC)
# mon_autocall.Calibration_Heston()
# calib = mon_autocall.get_calibration()
# print(calib)
# mon_autocall.CoursSpot()
# mon_autocall.MonteCarlo()
# prix = mon_autocall.get_prix()
# prix_dollar = mon_autocall.get_prix_dollar()
# print("Mon autocall vaut {:.2%} du nominal soit {:.2f}$".format(prix, prix_dollar))


# V.smile_Fwd_a_matu()
# smile_Fwd_a_matu = V.get_smile_Fwd_a_matu()

# vol_loc = vol_local_a_matu(300, echeancier_simulation[1], echeancier_simulation, smile_Fwd_a_matu, "call", 0.04)
# volatilite_loc = vol_local_square(190, echeancier_simulation[5], echeancier_simulation, smile, "call", 0.04, mat.get_T())
# print(volatilite_loc)
# print(vol_loc)
