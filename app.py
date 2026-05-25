import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title='Análise de Combustíveis no Brasil',
    page_icon='🛢️',
    layout='wide'
)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.title('🛢️ Análise de Preços de Combustíveis no Brasil')
st.markdown('**Projeto G2 — Tema 11 | Linguagem de Programação | Sistemas de Informação**')
st.markdown('Grupo 11: Lucas Muniz Miranda & Thiago Matheus')
st.divider()

# ── Carregamento dos dados ─────────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    df = pd.read_csv('dados/simulacao_precos_combustiveis_brasil.csv')
    df['data'] = pd.to_datetime(df['data'])
    cols_num = ['preco_medio', 'preco_minimo', 'preco_maximo',
                'variacao_mensal', 'inflacao', 'cotacao_petroleo', 'consumo_estimado']
    df[cols_num] = df[cols_num].apply(pd.to_numeric, errors='coerce')
    df = df.drop_duplicates()
    df = df[df['preco_medio'] > 0]
    df['trimestre'] = df['data'].dt.quarter
    df['ano_mes'] = df['data'].dt.to_period('M').astype(str)
    df['amplitude_preco'] = df['preco_maximo'] - df['preco_minimo']
    return df

df = carregar_dados()

# ── Filtros na sidebar ─────────────────────────────────────────────────────────
st.sidebar.header('🔎 Filtros')

anos = sorted(df['ano'].unique())
ano_sel = st.sidebar.multiselect('Ano', anos, default=anos)

meses = sorted(df['mes'].unique())
mes_sel = st.sidebar.multiselect('Mês', meses, default=meses)

regioes = sorted(df['regiao'].unique())
regiao_sel = st.sidebar.multiselect('Região', regioes, default=regioes)

estados = sorted(df['uf'].unique())
estado_sel = st.sidebar.multiselect('Estado (UF)', estados, default=estados)

combustiveis = sorted(df['combustivel'].unique())
comb_sel = st.sidebar.multiselect('Combustível', combustiveis, default=combustiveis)

niveis = sorted(df['nivel_preco'].unique())
nivel_sel = st.sidebar.multiselect('Nível de Preço', niveis, default=niveis)

# ── Aplica filtros ─────────────────────────────────────────────────────────────
df_f = df[
    df['ano'].isin(ano_sel) &
    df['mes'].isin(mes_sel) &
    df['regiao'].isin(regiao_sel) &
    df['uf'].isin(estado_sel) &
    df['combustivel'].isin(comb_sel) &
    df['nivel_preco'].isin(nivel_sel)
]

if df_f.empty:
    st.warning('Nenhum dado encontrado com os filtros selecionados.')
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.subheader('📊 KPIs — Indicadores-Chave de Desempenho')

preco_medio_nacional  = df_f['preco_medio'].mean()
combustivel_mais_caro = df_f.groupby('combustivel')['preco_medio'].mean().idxmax()
preco_comb_mais_caro  = df_f.groupby('combustivel')['preco_medio'].mean().max()
estado_mais_caro      = df_f.groupby('uf')['preco_medio'].mean().idxmax()
preco_estado_caro     = df_f.groupby('uf')['preco_medio'].mean().max()
maior_variacao_row    = df_f.loc[df_f['variacao_mensal'].abs().idxmax()]
consumo_total         = df_f['consumo_estimado'].sum()
regiao_mais_cara      = df_f.groupby('regiao')['preco_medio'].mean().idxmax()

c1, c2, c3 = st.columns(3)
c1.metric('💰 Preço Médio Nacional', f'R$ {preco_medio_nacional:.2f}')
c2.metric('🔥 Combustível Mais Caro', f'{combustivel_mais_caro}', f'R$ {preco_comb_mais_caro:.2f}')
c3.metric('📍 Estado Mais Caro', estado_mais_caro, f'R$ {preco_estado_caro:.2f}')

c4, c5, c6 = st.columns(3)
c4.metric('📈 Maior Variação Mensal', f'{maior_variacao_row["variacao_mensal"]:.2f}%',
          f'{maior_variacao_row["combustivel"]} — {maior_variacao_row["uf"]}')
c5.metric('⛽ Consumo Estimado Total', f'{consumo_total:,.0f} L')
c6.metric('🗺️ Região Mais Cara', regiao_mais_cara)

st.divider()

# ── Visualização 1 — Linha temporal ───────────────────────────────────────────
st.subheader('📈 Visualização 1 — Linha Temporal: Evolução dos Preços')
st.caption('Evolução do preço médio ao longo dos anos, separado por tipo de combustível.')

evolucao = df_f.groupby(['ano', 'combustivel'])['preco_medio'].mean().reset_index()
fig1, ax1 = plt.subplots(figsize=(12, 5))
for comb in evolucao['combustivel'].unique():
    dados = evolucao[evolucao['combustivel'] == comb]
    ax1.plot(dados['ano'], dados['preco_medio'], marker='o', linewidth=2, label=comb)
ax1.set_title('Evolução do Preço Médio por Combustível', fontsize=14, fontweight='bold')
ax1.set_xlabel('Ano')
ax1.set_ylabel('Preço Médio (R$/litro)')
ax1.legend(title='Combustível')
ax1.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig1)
plt.close()

st.divider()

# ── Visualização 2 — Barras por estado ────────────────────────────────────────
st.subheader('🗺️ Visualização 2 — Barras por Estado: Comparação Regional')
st.caption('Comparação do preço médio entre os estados brasileiros.')

preco_estado = df_f.groupby('uf')['preco_medio'].mean().sort_values(ascending=False).reset_index()
fig2, ax2 = plt.subplots(figsize=(14, 5))
bars = ax2.bar(preco_estado['uf'], preco_estado['preco_medio'],
               color=sns.color_palette('RdYlGn_r', len(preco_estado)))
for bar, valor in zip(bars, preco_estado['preco_medio']):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.05,
             f'R${valor:.2f}', ha='center', va='bottom', fontsize=8)
ax2.set_title('Preço Médio por Estado (UF)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Estado')
ax2.set_ylabel('Preço Médio (R$/litro)')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)
plt.close()

st.divider()

# ── Visualização 3 — Barras por combustível ───────────────────────────────────
st.subheader('⛽ Visualização 3 — Barras por Combustível: Comparação Energética')
st.caption('Comparação do preço médio entre os diferentes tipos de combustível.')

preco_comb = df_f.groupby('combustivel')['preco_medio'].mean().sort_values(ascending=False).reset_index()
fig3, ax3 = plt.subplots(figsize=(9, 5))
bars3 = ax3.bar(preco_comb['combustivel'], preco_comb['preco_medio'],
                color=sns.color_palette('Blues_r', len(preco_comb)))
for bar, valor in zip(bars3, preco_comb['preco_medio']):
    ax3.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.05,
             f'R${valor:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax3.set_title('Preço Médio por Tipo de Combustível', fontsize=14, fontweight='bold')
ax3.set_xlabel('Combustível')
ax3.set_ylabel('Preço Médio (R$/litro)')
plt.tight_layout()
st.pyplot(fig3)
plt.close()

st.divider()

# ── Visualização 4 — Heatmap mensal ───────────────────────────────────────────
st.subheader('🔥 Visualização 4 — Heatmap Mensal: Evolução Temporal')
st.caption('Mapa de calor com o preço médio por mês e ano.')

heatmap_data = df_f.groupby(['ano', 'mes'])['preco_medio'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='ano', columns='mes', values='preco_medio')
heatmap_pivot.columns = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][:len(heatmap_pivot.columns)]
fig4, ax4 = plt.subplots(figsize=(14, 6))
sns.heatmap(heatmap_pivot, annot=True, fmt='.2f', cmap='YlOrRd',
            linewidths=0.5, linecolor='white',
            cbar_kws={'label': 'Preço Médio (R$/litro)'}, ax=ax4)
ax4.set_title('Heatmap — Preço Médio Mensal por Ano', fontsize=14, fontweight='bold')
ax4.set_xlabel('Mês')
ax4.set_ylabel('Ano')
plt.tight_layout()
st.pyplot(fig4)
plt.close()

st.divider()

# ── Visualização 5 — Dispersão inflação x preço ───────────────────────────────
st.subheader('📉 Visualização 5 — Dispersão: Inflação x Preço')
st.caption('Correlação entre o índice de inflação e o preço médio dos combustíveis.')

fig5, ax5 = plt.subplots(figsize=(11, 6))
cores = sns.color_palette('tab10', len(df_f['combustivel'].unique()))
for comb, cor in zip(df_f['combustivel'].unique(), cores):
    subset = df_f[df_f['combustivel'] == comb]
    ax5.scatter(subset['inflacao'], subset['preco_medio'],
                label=comb, alpha=0.5, s=30, color=cor)
z = np.polyfit(df_f['inflacao'], df_f['preco_medio'], 1)
p = np.poly1d(z)
x_linha = np.linspace(df_f['inflacao'].min(), df_f['inflacao'].max(), 200)
ax5.plot(x_linha, p(x_linha), color='black', linewidth=2, linestyle='--', label='Tendência geral')
correlacao = df_f['inflacao'].corr(df_f['preco_medio'])
ax5.text(0.02, 0.95, f'Correlação: {correlacao:.3f}',
         transform=ax5.transAxes, fontsize=11, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
ax5.set_title('Dispersão — Inflação x Preço Médio', fontsize=14, fontweight='bold')
ax5.set_xlabel('Inflação (%)')
ax5.set_ylabel('Preço Médio (R$/litro)')
ax5.legend(title='Combustível')
plt.tight_layout()
st.pyplot(fig5)
plt.close()

st.divider()

# ── Visualização 6 — Tabela dinâmica ──────────────────────────────────────────
st.subheader('📋 Visualização 6 — Tabela Dinâmica: Exploração Detalhada')
st.caption('Preço médio agrupado por região, combustível e ano.')

tabela = df_f.pivot_table(
    values='preco_medio',
    index=['regiao', 'combustivel'],
    columns='ano',
    aggfunc='mean'
).round(2)
tabela['Média Geral'] = tabela.mean(axis=1).round(2)
st.dataframe(tabela.style.background_gradient(cmap='YlOrRd').format('R$ {:.2f}'),
             use_container_width=True)

st.divider()

# ── Interpretação e Conclusão ──────────────────────────────────────────────────
st.subheader('✍️ Interpretação dos Resultados')
st.markdown("""
- **Evolução temporal:** os preços apresentaram tendência de alta ao longo de 2015–2024, com picos entre 2021 e 2022 influenciados pela alta do petróleo no pós-pandemia.
- **Comparação estadual:** estados do Norte e Nordeste tendem a preços mais elevados, reflexo dos custos logísticos de distribuição.
- **Comparação por combustível:** Gasolina e GNV figuram entre os mais caros, enquanto o Etanol apresenta maior volatilidade pela dependência da safra.
- **Heatmap mensal:** o segundo semestre concentra os maiores preços médios, associados ao aumento da demanda.
- **Inflação x Preço:** há correlação positiva entre inflação e preços, confirmando combustíveis como componente relevante da inflação brasileira.
""")

st.subheader('🏁 Conclusão Executiva')
st.markdown("""
**Principais achados:**
- O preço médio nacional cresceu significativamente no período analisado
- Existem disparidades regionais relevantes, com estados do Norte pagando mais caro
- A inflação possui correlação positiva com os preços dos combustíveis
- Os anos de 2021 e 2022 concentraram os maiores níveis de preço e instabilidade

**Recomendações:**
- Políticas de estabilização devem considerar as diferenças regionais
- O monitoramento da cotação do petróleo é essencial para antecipar variações
- Incentivo a combustíveis alternativos pode reduzir a dependência da Gasolina

> Projeto acadêmico — Linguagem de Programação | Sistemas de Informação | Grupo 11
""")
