
import random

finished = False

class call_counter( object ):
    def __init__( self, name, sub ):
        self.name = name
        self.sub = sub
        self.count = 0
        
    def __call__( self ):
        if random.randint( 0, 2 ) > 0:
            self.count += 1
        else:
            self.sub()
            
def done( ):
    global finished
    finished = True

p = call_counter( 'p', done )
n = call_counter( 'n', p )
s = call_counter( 's', n )
b = call_counter( 'b', s )

while not finished: b()

for o in b,n,s,p: print o.name, o.count
