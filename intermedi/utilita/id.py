__author__ = 'fabio.lana'

lista_rp = [25, 50, 100, 200, 500, 1000]
lista_rp.append(8000)
print id(lista_rp)

lista_1 = []
lista_1.append(lista_rp)
lista_1.append(lista_rp)
print id(lista_1)

print lista_rp
print lista_1