import numpy as np

class FitzhughNagumo(object):
    r"""
    Fitzhugh-Nagumo neural model

    .. math::

        \frac{du}{dt} = u-\frac{u^{3}}{3}-v+I\\
        \frac{dv}{dt} = \frac{1}{\tau}(u+a-b \cdot v)

    * u : Membrane potential
    * v : Recovery variable
    * t : Time
    * tau : Time scale
    * I : Constant stimulus current
    * a,b : Parameters

    """

    def __init__(self, a, b, I, tau):
        """ initialize reaction parameter

        """

        self.a = a
        self.b = b
        self.I = I
        self.tau = tau

    def roots(self):
        r"""
        solve fixed points and keep only the roots with real values
        
        the polynomial equation to solve

        .. math::

            1                     v^{3}
            + 0                   v^{2}
            - (\frac{1}{b} - 1)   v^{1}
            - (\frac{a}{b} + I)   v^{0}
            = 0

        Returns
        --------
        roots : list
            the fixed point(s) with real values

        """
        
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


