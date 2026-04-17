import streamlit as st                                          # librarie pentru interfata web
import numpy as np                                              # librarie numerica
import pandas as pd                                             # librarie pentru tabele

                                                                # CONFIGURARE PAGINA SI DESIGN 
st.set_page_config(page_title="Problema Transporturilor", layout="wide")

st.markdown("""
    <style>
    .title-box { background-color: #FFC0CB; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .title-text { color: #FF00FF; font-size: 55px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .authors-box { color: #FF00FF; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #FF00FF; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #FF00FF; line-height: 1.6; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)                                    # design css baby pink si magenta

st.markdown('''
    <div class="title-box">
        <p class="title-text">🚚📦 Problema Transporturilor 📦🚚</p>
    </div>
''', unsafe_allow_html=True)                                    # afisare titlu principal cu stickere

st.markdown('''
    <div class="authors-box">
        <div class="authors-title">Facultatea de Științe Aplicate</div>
        <div class="authors-names">
            Dedu Anișoara-Nicoleta, 1333a<br>
            Dumitrescu Andreea Mihaela, 1333a<br>
            Iliescu Daria-Gabriela, 1333a<br>
            Lungu Ionela-Diana, 1333a
        </div>
    </div>
''', unsafe_allow_html=True)                                    # detalii despre echipa 

st.divider()                                                    # linie de separare

                                                                # ALGORITMI PROBLEMA TRANSPORTURILOR

def echilibreaza_problema(C, A, B):                             # pas 1: verificam daca e PTE (Echilibrata)
    sum_A = sum(A)
    sum_B = sum(B)
    C_echil = np.array(C, dtype=float)
    A_echil = list(A)
    B_echil = list(B)
    
    if sum_A > sum_B:                                           # cerere < oferta -> destinatie fictiva
        B_echil.append(sum_A - sum_B)
        coloana_zero = np.zeros((C_echil.shape[0], 1))
        C_echil = np.hstack((C_echil, coloana_zero))
        return C_echil, A_echil, B_echil, "Destinație Fictivă"
    elif sum_B > sum_A:                                         # oferta < cerere -> sursa fictiva
        A_echil.append(sum_B - sum_A)
        linie_zero = np.zeros((1, C_echil.shape[1]))
        C_echil = np.vstack((C_echil, linie_zero))
        return C_echil, A_echil, B_echil, "Sursă Fictivă"
    return C_echil, A_echil, B_echil, "Echilibrată"

def coltul_nv(A, B):                                            # pas 2: metoda coltului N-V
    m, n = len(A), len(B)
    X = np.zeros((m, n))
    baza = []
    
    a_temp, b_temp = A.copy(), B.copy()
    i, j = 0, 0
    
    while i < m and j < n:
        minim = min(a_temp[i], b_temp[j])
        X[i, j] = minim
        baza.append((i, j))
        a_temp[i] -= minim
        b_temp[j] -= minim
        
        if a_temp[i] == 0 and b_temp[j] == 0:                   # degenerare la N-V
            if i + 1 < m:                                       # punem un 0 fortat ca sa pastram baza (m+n-1)
                baza.append((i + 1, j))
            i += 1
            j += 1
        elif a_temp[i] == 0:
            i += 1
        else:
            j += 1
            
    return X, baza

def calculeaza_potentiale(C, baza, m, n):                       # pas 3: metoda potentialelor (u, v)
    u = [None] * m
    v = [None] * n
    u[0] = 0                                                    # fixam u1 = 0
    
    while None in u or None in v:
        for (i, j) in baza:
            if u[i] is not None and v[j] is None:
                v[j] = C[i, j] - u[i]
            elif v[j] is not None and u[i] is None:
                u[i] = C[i, j] - v[j]
    return u, v

def calculeaza_delta(C, u, v, m, n):                            # calculam costurile indirecte (Dj)
    Delta = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            Delta[i, j] = C[i, j] - (u[i] + v[j])
    return Delta

def gaseste_ciclu(celule_valide, start):                        # gasim poligonul pentru actualizare
    def dfs(curent, drum, e_orizontal):
        if len(drum) >= 4 and curent == start:
            return drum[:-1]                                    # returnam drumul fara dublura de start
        for nod in celule_valide:
            if nod not in drum or (nod == start and len(drum) >= 4):
                acelasi_rand = (nod[0] == curent[0])
                aceeasi_col = (nod[1] == curent[1])
                
                if e_orizontal and acelasi_rand and not aceeasi_col:
                    rez = dfs(nod, drum + [nod], False)
                    if rez: return rez
                elif not e_orizontal and aceeasi_col and not acelasi_rand:
                    rez = dfs(nod, drum + [nod], True)
                    if rez: return rez
        return None

    # cautam un ciclu plecand intai pe orizontala, apoi pe verticala
    return dfs(start, [start], True) or dfs(start, [start], False)

                                                                # INTERFATA UTILIZATOR

st.sidebar.header("⚙️ Setări Dimensiuni Tabel")
m_surse = st.sidebar.number_input("Număr Furnizori (A_i)", 2, 6, 3)
n_dest = st.sidebar.number_input("Număr Beneficiari (B_j)", 2, 6, 4)

st.markdown("<h3 style='color: #FF00FF;'>1. Datele Problemei</h3>", unsafe_allow_html=True)

col_c, col_ab = st.columns([2, 1])

with col_c:
    st.write("**Matricea Costurilor Unitare (C_ij):**")
    C_default = np.random.randint(1, 10, size=(m_surse, n_dest))
    df_C = pd.DataFrame(C_default, index=[f"A{i+1}" for i in range(m_surse)], columns=[f"B{j+1}" for j in range(n_dest)])
    C_input = st.data_editor(df_C, use_container_width=True).values

with col_ab:
    st.write("**Disponibil (Oferta A_i):**")
    A_default = np.array([20, 30, 20][:m_surse])
    if len(A_default) < m_surse: A_default = np.pad(A_default, (0, m_surse - len(A_default)), constant_values=20)
    df_A = pd.DataFrame(A_default, index=[f"A{i+1}" for i in range(m_surse)], columns=["Oferta"])
    A_input = st.data_editor(df_A, use_container_width=True).values.flatten().tolist()

    st.write("**Necesar (Cererea B_j):**")
    B_default = np.array([10, 20, 20, 20][:n_dest])
    if len(B_default) < n_dest: B_default = np.pad(B_default, (0, n_dest - len(B_default)), constant_values=15)
    df_B = pd.DataFrame(B_default, index=[f"B{j+1}" for j in range(n_dest)], columns=["Cerere"])
    B_input = st.data_editor(df_B, use_container_width=True).values.flatten().tolist()


if st.button("🚀 Rezolvă Problema de Transport", type="primary", use_container_width=True):
    st.divider()
    
                                                                # PASUL 1: ECHILIBRAREA
    st.markdown("<h3 style='color: #FF00FF;'>2. Verificarea Echilibrului ($\Sigma D = \Sigma N$)</h3>", unsafe_allow_html=True)
    C_lucru, A_lucru, B_lucru, status = echilibreaza_problema(C_input, A_input, B_input)
    
    st.write(f"$\Sigma A_i$ (Oferta) = **{sum(A_input)}** | $\Sigma B_j$ (Cererea) = **{sum(B_input)}**")
    
    if status == "Echilibrată":
        st.success("✅ Problema este deja o **PTE** (Problemă de Transport Echilibrată).")
    else:
        st.warning(f"⚠️ Dezechilibru! S-a adăugat o **{status}** pentru a forma o PTE.")
        st.write("**Noua matrice a costurilor (cu costuri 0 pentru elementele fictive):**")
        df_echil = pd.DataFrame(C_lucru)
        st.dataframe(df_echil, use_container_width=True)

    m, n = len(A_lucru), len(B_lucru)

                                                                # PASUL 2: SOLUTIA INITIALA
    st.markdown("<h3 style='color: #FF00FF;'>3. Soluția Inițială de Bază (Metoda Colțului N-V)</h3>", unsafe_allow_html=True)
    X_baza, celule_baza = coltul_nv(A_lucru, B_lucru)
    
    cost_initial = np.sum(X_baza * C_lucru)
    st.write("Alocările inițiale $X_{ij}$:")
    df_init = pd.DataFrame(X_baza, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    st.dataframe(df_init.style.highlight_between(left=0.01, color='#F8C8DC'), use_container_width=True) # highlight alocarile
    st.info(f"💰 Costul de transport inițial: **{cost_initial} u.m.**")

                                                                # PASUL 3: ITERATIILE MODI
    st.markdown("<h3 style='color: #FF00FF;'>4. Optimizarea Soluției (Algoritmul MODI / Potențialelor)</h3>", unsafe_allow_html=True)
    
    iteratie = 1
    max_iter = 20                                               # limita de siguranta
    
    while iteratie <= max_iter:
        u, v = calculeaza_potentiale(C_lucru, celule_baza, m, n)
        Delta = calculeaza_delta(C_lucru, u, v, m, n)
        
        # verificam conditia de optim (toate Delta_ij >= 0)
        este_optim = True
        min_delta = 0
        intrata = None
        
        for i in range(m):
            for j in range(n):
                if (i, j) not in celule_baza:
                    if Delta[i, j] < min_delta:
                        min_delta = Delta[i, j]
                        intrata = (i, j)
                        este_optim = False
                        
        if este_optim:
            st.success(f"✅ S-a atins soluția optimă la iterația {iteratie-1} ($\Delta_{{ij}} \ge 0$).")
            break
            
        st.markdown(f"#### Iterația {iteratie}")
        
        col_uv, col_delta = st.columns(2)
        with col_uv:
            st.write(f"**Potențiale:** $u_i =$ {u}, $v_j =$ {v}")
        with col_delta:
            st.write(f"**Cea mai negativă valoare:** $\Delta_{{{intrata[0]+1}, {intrata[1]+1}}} = {min_delta}$")
            
        # gasim circuitul pentru a rearanja alocarile
        celule_valide = celule_baza + [intrata]
        circuit = gaseste_ciclu(celule_valide, intrata)
        
        if circuit is None:
            st.error("Eroare de degenerare / ciclu imposibil de găsit.")
            break
            
        # celulele cu 'minus' se afla pe pozitiile impare in lista circuitului
        celule_minus = circuit[1::2]
        valori_minus = [X_baza[r, c] for (r, c) in celule_minus]
        theta = min(valori_minus)
        iesita = celule_minus[valori_minus.index(theta)]
        
        st.write(f"🔄 **Circuit:** {[(r+1, c+1) for r,c in circuit]}")
        st.write(f"Pasul $\\theta = {theta}$. Celula care iese din bază: ({iesita[0]+1}, {iesita[1]+1})")
        
        # aplicam cantitatea theta pe circuit (+, -, +, -)
        semn = 1
        for (r, c) in circuit:
            X_baza[r, c] += semn * theta
            semn *= -1
            
        celule_baza.remove(iesita)
        celule_baza.append(intrata)
        
        iteratie += 1

                                                                # PASUL 4: REZULTATE FINALE
    st.markdown("---")
    st.markdown("<h3 style='color: #FF00FF; text-align: center;'>📦 REZULTAT FINAL 📦</h3>", unsafe_allow_html=True)
    
    cost_final = np.sum(X_baza * C_lucru)
    
    st.write("**Planul Optim de Transport ($X_{ij}$):**")
    df_final = pd.DataFrame(X_baza, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    st.dataframe(df_final.style.highlight_between(left=0.01, color='#FFC0CB'), use_container_width=True)
    
    st.markdown(f"<h2 style='color: #C71585; text-align: center;'>Cost Total Minim: {cost_final} u.m.</h2>", unsafe_allow_html=True)
    st.balloons()
