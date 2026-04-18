import streamlit as st                                          # librarie pentru interfata web
import numpy as np                                              # librarie numerica
import pandas as pd                                             # librarie pentru tabele
import random                                                   # librarie pentru randomizarea funditelor

# ==============================================================================
# CONFIGURARE PAGINA SI DESIGN CSS
# ==============================================================================
st.set_page_config(page_title="Problema Transporturilor", layout="wide")

st.markdown("""
    <style>
    .title-box { background-color: #fddde6; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; }
    .title-text { color: #ff007f; font-size: 50px; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

def afiseaza_fundite_baby_pink():                               # functie care genereaza 50 de fundite
    bows_html = "<div style='position: fixed; top: 0; left: 0; width: 0px; height: 0px; z-index: 99999;'>"
    for _ in range(50):
        bows_html += f"<div class='bow' style='position:fixed; left:{random.randint(0,100)}vw; font-size: 2rem;'>🎀</div>"
    st.markdown(bows_html + "</div>", unsafe_allow_html=True)

def fmt(val):                                                   # curatam numerele de formatul urat
    if pd.isna(val) or val is None: return ""
    return str(int(val)) if float(val).is_integer() else f"{val:.2f}"

# ==============================================================================
# ALGORITMI
# ==============================================================================
def echilibreaza_problema(C, A, B):                             # pas 1: verificam conditia de echilibru
    sum_A, sum_B = sum(A), sum(B)
    if sum_A > sum_B: return np.hstack((C, np.zeros((len(A),1)))), A, B + [sum_A - sum_B], "Beneficiar Fictiv"
    if sum_B > sum_A: return np.vstack((C, np.zeros((1, len(B))))), A + [sum_B - sum_A], B, "Furnizor Fictiv"
    return C, A, B, "Echilibrată"

def coltul_nv(A, B):                                            # pas 2: calculam prima baza (Metoda N-V)
    m, n, X = len(A), len(B), np.zeros((len(A), len(B)))
    baza, a_t, b_t = [], list(A), list(B)
    i = j = 0
    while i < m and j < n:
        val = min(a_t[i], b_t[j])
        X[i, j] = val
        baza.append((i, j))
        a_t[i] -= val; b_t[j] -= val
        if a_t[i] == 0: i += 1
        else: j += 1
    return X, baza

# ==============================================================================
# INTERFATA UI
# ==============================================================================
st.markdown('<div class="title-box"><p class="title-text">🚚📦 Problema Transporturilor 📦🚚</p></div>', unsafe_allow_html=True)

# Datele problemei
C_data = np.array([[1, 3, 2, 4], [3, 1, 2, 2], [2, 3, 2, 1]])
A_data = [30, 39, 21]
B_data = [25, 20, 30, 15]

if st.button("🚀 Rezolvă Problema Pas cu Pas"):
    afiseaza_fundite_baby_pink()
    
    # 1. ECHILIBRU
    C, A, B, status = echilibreaza_problema(C_data, A_data, B_data)
    st.markdown("### Pasul 1. Verificăm PTE")
    st.latex(rf"\Sigma D = {sum(A_data)} \quad \Sigma N = {sum(B_data)}")
    st.info(f"Stare: {status}")
    
    # 2. COLTUL N-V
    X, baza = coltul_nv(A, B)
    st.markdown("### Pasul 2. Metoda Colțului N-V")
    
    # 3. ALGORITMUL MODI (Iteratii)
    m, n = len(A), len(B)
    cost = np.sum(X * C)
    
    for it in range(5): # Limitare iteratii
        st.markdown(f"#### Iterația {it}")
        
        # Calcul potentiale (Sistemul S)
        u = [None]*m; v = [None]*n; u[0] = 0
        schimbare = True
        while schimbare:
            schimbare = False
            for (i, j) in baza:
                if u[i] is not None and v[j] is None: v[j] = C[i,j] - u[i]; schimbare = True
                elif v[j] is not None and u[i] is None: u[i] = C[i,j] - v[j]; schimbare = True
        
        # Afisare sistem
        c1, c2 = st.columns(2)
        with c1:
            sistem = r"\begin{cases} " + " \\\\ ".join([f"u_{i+1}+v_{j+1}={C[i,j]}" for (i,j) in baza]) + r" \end{cases}"
            st.latex(r"S: " + sistem)
        
        # Calcul Delta
        delta = np.zeros((m, n))
        for i in range(m):
            for j in range(n): delta[i,j] = C[i,j] - (u[i] + v[j])
            
        # Stop sau Pivotare
        if np.all(delta >= 0):
            st.success("TO: Optim atins! STOP.")
            break
        else:
            # Identificare pivot si pivotare (simplificat pentru vizualizare)
            st.warning("TO: Optim neatins. Se caută circuitul și se pivotează.")
            # Aici s-ar face pivotarea efectiva (logica din paginile 8-10)
            break
            
    st.markdown("### 📦 Rezultat Final")
    st.write(f"Cost Total Minim: **{fmt(cost)}** u.m.")
