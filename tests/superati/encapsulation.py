__author__ = 'fabio.lana'

class Counter(object):
    number = 0
    def __init__(self):
        type(self).number += 1

    def __del__(self):
        type(self).number -= 1

class Account(Counter):

    def __init__(self,
                 account_holder,
                 account_nunmber,
                 balance,
                 account_current=1500):

        self.account_holder = account_holder
        Counter.__init__(self)
