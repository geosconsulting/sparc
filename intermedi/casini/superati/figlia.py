__author__ = 'fabio.lana'
from intermedi.casini.superati.madre import Madre

class Figlia(Madre):

   def test(self):
        super(Figlia, self).test()
        print "Valori contenuti nella lista in madre " + str(self.lista)
        print self.pippo

x = Figlia("Valore instanziato da Figlia")
x.test()
