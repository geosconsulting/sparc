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

x = ChildClass("'Come t'antitoli")
x.test()
