import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry  # Installer avec : pip install tkcalendar
import datetime

class PricerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pricer d'Options")
        self.geometry("600x550")
        
        # Création du Notebook pour gérer les onglets
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')
        
        # Onglet Accueil
        accueil_frame = ttk.Frame(notebook)
        notebook.add(accueil_frame, text="Accueil")
        accueil_label = ttk.Label(accueil_frame, text="Bienvenue sur le pricer d'options", font=("Arial", 14))
        accueil_label.pack(pady=20, padx=20)
        quit_button = ttk.Button(accueil_frame, text="Quitter", command=self.quit)
        quit_button.pack(pady=10)
        
        # Onglet Dates (placé juste après Accueil)
        date_frame = ttk.Frame(notebook)
        notebook.add(date_frame, text="Dates")
        # Sélection de la date de début
        start_date_label = ttk.Label(date_frame, text="Date de début :")
        start_date_label.pack(pady=5)
        self.start_date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.start_date_entry.pack(pady=5)
        # Sélection de la date de fin
        end_date_label = ttk.Label(date_frame, text="Date de fin :")
        end_date_label.pack(pady=5)
        self.end_date_entry = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.end_date_entry.pack(pady=5)
        # Bouton radio pour sélectionner la méthode de calcul
        method_label = ttk.Label(date_frame, text="Méthode de calcul du nombre d'années :")
        method_label.pack(pady=5)
        self.daycount_method = tk.StringVar(value="30/360")  # valeur par défaut
        methods = ["30/360", "30/365", "30/365.25", "exact/360", "exact/365", "exact/365.25"]
        for m in methods:
            rb = ttk.Radiobutton(date_frame, text=m, value=m, variable=self.daycount_method)
            rb.pack(anchor='w', padx=20)
        # Bouton pour calculer la maturité en années
        calc_button = ttk.Button(date_frame, text="Calculer Maturité", command=self.calculer_maturite)
        calc_button.pack(pady=10)
        # Label pour afficher la maturité calculée
        self.maturite_label = ttk.Label(date_frame, text="")
        self.maturite_label.pack(pady=5)
        
        # Onglet Equity Options
        equity_frame = ttk.Frame(notebook)
        notebook.add(equity_frame, text="Equity Options")
        equity_label = ttk.Label(equity_frame, text="Ici, vous pourrez pricer les options sur actions.", font=("Arial", 12))
        equity_label.pack(pady=10, padx=20)
        # Champ de saisie pour la maturité
        equity_maturity_label = ttk.Label(equity_frame, text="Maturité (en années) :")
        equity_maturity_label.pack(pady=5)
        self.equity_maturity_entry = ttk.Entry(equity_frame)
        self.equity_maturity_entry.pack(pady=5)
        # Champ de saisie pour le strike
        equity_strike_label = ttk.Label(equity_frame, text="Strike :")
        equity_strike_label.pack(pady=5)
        self.equity_strike_entry = ttk.Entry(equity_frame)
        self.equity_strike_entry.pack(pady=5)
        # Bouton pour afficher la prime
        equity_button = ttk.Button(equity_frame, text="Afficher Prime", command=self.afficher_prime_equity)
        equity_button.pack(pady=10)
        # Label pour afficher la prime calculée
        self.equity_prime_label = ttk.Label(equity_frame, text="")
        self.equity_prime_label.pack(pady=5)
        
        # Onglet FX Options
        fx_frame = ttk.Frame(notebook)
        notebook.add(fx_frame, text="FX Options")
        fx_label = ttk.Label(fx_frame, text="Ici, vous pourrez pricer les options sur devises.", font=("Arial", 12))
        fx_label.pack(pady=10, padx=20)
        # Champ de saisie pour la maturité
        fx_maturity_label = ttk.Label(fx_frame, text="Maturité (en années) :")
        fx_maturity_label.pack(pady=5)
        self.fx_maturity_entry = ttk.Entry(fx_frame)
        self.fx_maturity_entry.pack(pady=5)
        # Champ de saisie pour le strike
        fx_strike_label = ttk.Label(fx_frame, text="Strike :")
        fx_strike_label.pack(pady=5)
        self.fx_strike_entry = ttk.Entry(fx_frame)
        self.fx_strike_entry.pack(pady=5)
        # Bouton pour afficher la prime
        fx_button = ttk.Button(fx_frame, text="Afficher Prime", command=self.afficher_prime_fx)
        fx_button.pack(pady=10)
        # Label pour afficher la prime calculée
        self.fx_prime_label = ttk.Label(fx_frame, text="")
        self.fx_prime_label.pack(pady=5)
        
        # Onglet Rate Options
        rate_frame = ttk.Frame(notebook)
        notebook.add(rate_frame, text="Rate Options")
        rate_label = ttk.Label(rate_frame, text="Ici, vous pourrez pricer les options sur taux.", font=("Arial", 12))
        rate_label.pack(pady=10, padx=20)
        # Champ de saisie pour la maturité
        rate_maturity_label = ttk.Label(rate_frame, text="Maturité (en années) :")
        rate_maturity_label.pack(pady=5)
        self.rate_maturity_entry = ttk.Entry(rate_frame)
        self.rate_maturity_entry.pack(pady=5)
        # Champ de saisie pour le strike
        rate_strike_label = ttk.Label(rate_frame, text="Strike :")
        rate_strike_label.pack(pady=5)
        self.rate_strike_entry = ttk.Entry(rate_frame)
        self.rate_strike_entry.pack(pady=5)
        # Bouton pour afficher la prime
        rate_button = ttk.Button(rate_frame, text="Afficher Prime", command=self.afficher_prime_rate)
        rate_button.pack(pady=10)
        # Label pour afficher la prime calculée
        self.rate_prime_label = ttk.Label(rate_frame, text="")
        self.rate_prime_label.pack(pady=5)
    
    def afficher_prime_equity(self):
        try:
            maturity = float(self.equity_maturity_entry.get())
            strike = float(self.equity_strike_entry.get())
            # Calcul fictif pour la prime (à adapter avec votre modèle)
            premium = (maturity + strike) / 10
            self.equity_prime_label.config(text=f"Prime: {premium:.2f}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques pour la maturité et le strike.")
    
    def afficher_prime_fx(self):
        try:
            maturity = float(self.fx_maturity_entry.get())
            strike = float(self.fx_strike_entry.get())
            premium = (maturity + strike) / 20
            self.fx_prime_label.config(text=f"Prime: {premium:.2f}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques pour la maturité et le strike.")
    
    def afficher_prime_rate(self):
        try:
            maturity = float(self.rate_maturity_entry.get())
            strike = float(self.rate_strike_entry.get())
            premium = (maturity + strike) / 30
            self.rate_prime_label.config(text=f"Prime: {premium:.2f}")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques pour la maturité et le strike.")
    
    def calculer_fraction(self, start_date, end_date, method):
        """
        Calcule le nombre d'années entre deux dates selon la méthode sélectionnée.
        Pour les méthodes "30/*", on applique la convention 30 jours par mois.
        Pour les méthodes "exact/*", on utilise le nombre de jours réels.
        """
        if method.startswith("30"):
            # Calcul selon la convention 30 jours par mois
            numerator = 360 * (end_date.year - start_date.year) \
                        + 30 * (end_date.month - start_date.month) \
                        + (end_date.day - start_date.day)
            denominator = float(method.split('/')[1])
            return numerator / denominator
        elif method.startswith("exact"):
            delta = (end_date - start_date).days
            denominator = float(method.split('/')[1])
            return delta / denominator
        else:
            # Méthode non reconnue (cas improbable)
            return (end_date - start_date).days / 365.25
    
    def calculer_maturite(self):
        try:
            start_date = self.start_date_entry.get_date()  # objet datetime.date
            end_date = self.end_date_entry.get_date()
            if end_date < start_date:
                messagebox.showerror("Erreur", "La date de fin doit être postérieure à la date de début.")
                return
            method = self.daycount_method.get()
            years = self.calculer_fraction(start_date, end_date, method)
            self.maturite_label.config(text=f"Maturité: {years:.2f} années")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

if __name__ == "__main__":
    app = PricerGUI()
    app.mainloop()





# 123456789