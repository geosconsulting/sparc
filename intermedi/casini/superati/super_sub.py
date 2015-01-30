__author__ = 'fabio.lana'

class ParentClass(object):

    def __init__(self, pippo):
        self.pippo = pippo
        self.x = [1,2,3]

    def test(self):
        print 'Im in parent class'

class ChildClass(ParentClass):

   def test(self):
        super(ChildClass, self).test()
        print "Value of x = " + str(self.x)
        print self.pippo

x = ChildClass("Come t'antitoli")
x.test()

from intermedi.casini.superati.encapsulation import Account
print Account.number

x = Account("Fabio",1221, 253)
#print x.public
#print x._protected
print Account.number

y = Account("Patty", 12121, 50)
print Account.number

print y.account_holder

del y
print Account.number