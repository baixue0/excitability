import numpy as np

class FitzhughNagumo(object):
    r'''
    Fitzhugh-Nagumo neural model

    .. math::

        \frac{du}{dt} = u-\frac{u^{3}}{3}-v+I\\
        \frac{dv}{dt} = \frac{1}{\tau}(u+a-b \cdot v)

    [u,v]: [Membrane potential, Recovery variable]
    a, b (float): Parameters.
    tau (float): Time scale.
    t (float): Time (Not used: autonomous system)
    I (float): Constant stimulus current. 

    Example::

        ode = FitzhughNagumo(a, b, I, tau)
    '''

    def __init__(self, a, b, I, tau):
        self.a = a
        self.b = b
        self.I = I
        self.tau = tau

    def roots(self):
        '''
        solve real fixed points
        :rtype: list
        '''
        #The coeficients of the polynomial equation are:
        #1           * v**3 
        #0           * v**2 
        #- (1/b - 1) * v**1 
        #- (a/b + I) * v**0
        
        coef = [1/3, 0, 1/self.b - 1, self.a/self.b - self.I]
        
        # We are only interested in real roots.
        # np.isreal(x) returns True only if x is real. 
        # The following line filter the list returned by np.roots
        # and only keep the real values. 
        roots = [np.real(r) for r in np.roots(coef) if np.isreal(r)]
        
        # We store the position of the equilibrium. 
        return [[r, (r+self.a)/self.b] for r in roots]

    def du(self,u,v):
        '''
        calculate temporal derivative of u at (u,v)
        '''
        return u-(u**3)/3-v + self.I

    def dv(self,u,v):
        '''
        calculate temporal derivative of v at (u,v)
        '''
        return (u+self.a-self.b*v)/self.tau


