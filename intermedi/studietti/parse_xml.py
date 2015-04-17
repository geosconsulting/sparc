__author__ = 'fabio.lana'
from bs4 import BeautifulSoup as bs

file_allenamento = file('fabiolana_17.04.2015_export.xml')
base_analisi = bs(file_allenamento)
#print zuppa.prettify()

#print base_analisi.result.distance.string
#print base_analisi.result.distance.parent.name
#print
gruppo_dei_risultati = base_analisi.result

# for child in gruppo_dei_risultati.children:
#     print(child)

# for child in gruppo_dei_risultati.descendants:
#     print(child)

valori_importanti = dict()
for illo in gruppo_dei_risultati:
    if illo.string is not None:
        if len(illo.string)>1:
            valori_importanti[illo.name] = illo.string

#print valori_importanti

#campionamenti = base_analisi.result.samples.children
#for campionamento in campionamenti:
#    print campionamento

valori_cuore = str(base_analisi.result.samples.contents[1].values.string).split(",")
valori_distanza = str(base_analisi.result.samples.contents[7].values.string).split(",")

#valori_convertiti = [float(i) for i in valori_cuore]

import matplotlib.pyplot as plt
fig1 = plt.figure(figsize=(8,4))

ax1 = fig1.add_subplot(111)
ax1.set_title('Heart Rate')
ax1.set_xlabel('Beats')
ax1.set_ylabel('Time')
plt.plot(valori_cuore)

plt.show()










