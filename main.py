import os
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from config import get_db_config
from postgres_service import PostgresDB
from statistics import median, stdev
from colorama import Fore,Style

load_dotenv()

if __name__ == "__main__":
  # usa configurações do .env via config.get_db_config()
  cfg = get_db_config()

  with PostgresDB(**cfg) as db:
    print(Fore.YELLOW+'Connection Searching.......',Style.RESET_ALL)
    if db.is_connected():
      print(Fore.GREEN+'Connected',Style.RESET_ALL,f'{os.getenv("PG_DBNAME")}')

    sql = '''SELECT relato
            FROM 
            base_validada;
            '''

    data_query_reports= db.execute(sql)

    sql = '''SELECT 
                  nomes_pessoais_rot_final,
                  cpfs_cnpjs_rot_final,
                  rg_rot_final,
                  telefones_rot_final,
                  emails_rot_final,
                  dados_bancarios_rot_final,
                  enderecos_rot_final
                  FROM base_validada
                  WHERE nomes_pessoais_rot_final IS NOT NULL OR
                  cpfs_cnpjs_rot_final IS NOT NULL OR
                  rg_rot_final IS NOT NULL OR
                  telefones_rot_final IS NOT NULL OR
                  emails_rot_final IS NOT NULL OR
                  dados_bancarios_rot_final IS NOT NULL OR
                  enderecos_rot_final IS NOT NULL;
          '''
    data_query_labels = db.execute(sql)

    db.close()

  columns_data = (
                   "NOME_PESSOAIS",
                   "CPFS_CNPJS",
                   "RG",
                   "TELEFONE",
                   "E-MAIL",
                   "DADOS_BANCARIOS",
                   "ENDERECOS")
  

  data_rotulos = [[] for _ in range(len(columns_data))]

  def count_tokens_bos(data):
    return [len(str(report).strip().split()) for report in data]

  def count_labels_bos(data):
    new_data = []
    for column in range(len(columns_data)):
      labels = [len(str(row[column]).split(',')) for row in data if row[column] is not None]
      new_data.append(labels)
    return new_data 

data_tokens_labels = count_labels_bos(data_query_labels)
data_tokens_reports = count_tokens_bos(data_query_reports)

media_tokens_reports = median(data_tokens_reports)
stdev_tokens_reports = stdev(data_tokens_reports)

fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10,4))

ax1.boxplot(
    [data_tokens_reports],               
    showmeans=True,
    meanline=False,
    meanprops=dict(marker='o', markersize=8),
)

ax1.plot(1, stdev_tokens_reports, 'd', markersize=10)

current_ticks = ax1.get_yticks()
new_ticks = np.unique(np.append(current_ticks, [media_tokens_reports, stdev_tokens_reports]))
new_ticks.sort()

ax1.set_yticks(new_ticks)
ax1.set_yticklabels([f"{t:.2f}" for t in new_ticks])

ax1.set_ylabel('Quantidade')
ax1.set_xlabel('Relatos')     
ax1.set_title('Análise de tokens por B.O')

ax1.set_ylim([0,1000])


ax2.boxplot(
    data_tokens_labels,
    showmeans=True,
    meanline=False,
    meanprops=dict(marker='o', markersize=8)
)

for i, lista in enumerate(data_tokens_labels, start=1):
    if len(lista) > 1:
        desvio = stdev(lista)
        ax2.plot(i, desvio, 'd', markersize=10)

ax2.set_ylabel('Quantidade')
ax2.set_xlabel('Rótulos')
ax2.set_title('Análise de tokens por rótulos')

ax2.set_xticks(range(1, len(columns_data) + 1))
ax2.set_xticklabels(columns_data, rotation=45, ha="right")

plt.tight_layout()
plt.show()
