# 1) pip install pandas mlxtend

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# 2) Definícia dát z Variant 5
data = {
    'Vek':         ['Mladý','Mladý','Mladý','Dospelý','Dospelý',
                    'Starý','Starý','Dospelý','Starý','Starý'],
    'Pohlavie':    ['Muž','Muž','Žena','Muž','Žena',
                    'Muž','Žena','Žena','Žena','Muž'],
    'Očný tlak':   ['Zvýšený','Zmenšený','Zmenšený','Zmenšený','Zmenšený',
                    'Zvýšený','Zmenšený','Normálny','Zmenšený','Normálny'],
    'Šošovky':     ['Hard','Nie','Soft','Hard','Soft',
                    'Soft','Soft','Nie','Soft','Nie']
}
df = pd.DataFrame(data)

# 3) One-hot encoding
df_enc = pd.get_dummies(df)

# 4) Nájdeme časté množiny so support ≥ 0.1 (1 prípad z 10)
freq = apriori(df_enc, min_support=0.1, use_colnames=True)

# 5) Vygenerujeme všetky možné pravidlá
rules = association_rules(freq, metric="confidence", min_threshold=0)

# 6) Filtrácia: hľadáme presne pravidlo
#    {Pohlavie_Žena, Očný tlak_Zmenšený} → {Šošovky_Soft}
target_ante = frozenset({'Pohlavie_Žena', 'Očný tlak_Zmenšený'})
target_cons = frozenset({'Šošovky_Soft'})

rule = rules[
    (rules['antecedents'] == target_ante) &
    (rules['consequents'] == target_cons)
]

print(rule[['antecedents','consequents','support','confidence','lift']])
