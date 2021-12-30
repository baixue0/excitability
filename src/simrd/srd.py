import numpy as np
from pde import PDEBase,MemoryStorage
class SRD(PDEBase):
    r"""
    solve two-variable reaction diffusion equations on 1d grid using the py-pde `solver <https://github.com/zwicker-group/py-pde>`_ 

    .. math::
 
        \frac{\partial u_{(x,t)}}{\partial t} = D_{u} \cdot \frac{\partial^2 u_{(x,t)}}{\partial x^2}+f_{u}(u_{(x,t)},v_{(x,t)})+\xi_{(x,t)}\\
        \frac{\partial v_{(x,t)}}{\partial t} = D_{v} \cdot \frac{\partial^2 v_{(x,t)}}{\partial x^2}+f_{v}(u_{(x,t)},v_{(x,t)})
    """

    def __init__(self, perturb_arr, ode=None, DuDv=(None,None)):
        """initialize parameters

        Parameters
        ----------
        perturb_arr : `numpy.ndarray`, (T,X), float
            used to construct a interpolator of noisy perturbation during simulation
        ode : object
            an instance of a class with ``roots``, ``du``, ``dv`` method
        DuDv : tuple
            diffusion rates of u, v respectively. (None,None) indicates not diffusion.

        Example
        --------

        .. code-block:: python

            ode = FitzhughNagumo(a, b, I, tau)#set reaction parameters
            eq = SRD(noisearr,ode=ode)# set predetermined perturbations
            arrtx = eq.solvetx()# solve partial differential equation

        """

        self.T, self.gridsize = arr.shape
        from scipy.interpolate import RegularGridInterpolator as interp
        self.perturb = interp((np.arange(self.T), np.arange(self.gridsize)), perturb_arr, method='nearest', bounds_error=False, fill_value=0)#interpolator

        self.ode = ode
        self.Du, self.Dv = DuDv # u,v diffusion rate
        self.bc = "natural" # boundary condition: vanishing derivative for non-periodic axis

        self.u0v0 = ode.roots()[0]#first fixed point
        
    def get_initial_state(self):
        """initialize grid 
        
        Returns
        --------
        initial state : `pde.FieldCollection`
            * made up of two `pde.ScalarField` representing u and v respectively
            * each `pde.ScalarField` is a 1-dimensional (X,) Cartesian grid with unit discretization
            * periodic boundary conditions

        """
        from pde import UnitGrid, ScalarField, FieldCollection
        return FieldCollection([ScalarField(UnitGrid(self.gridsize,periodic=True), w) for w in self.u0v0])

    def evolution_rate(self, state, t=0):
        '''
        update the state by adding changes in u,v level from perturb, react, diffuse
        '''

        u, v = state
        rhs = state.copy()
        rhs[0],rhs[1] = 0,0

        pts = list(zip(np.full(self.gridsize,t),np.arange(self.gridsize)))
        rhs[0] += self.perturb(pts)# perturb

        if self.ode is not None:# react
            rhs[0] += self.ode.du(u,v)
            rhs[1] += self.ode.dv(u,v)

        if self.Du is not None:# diffuse
            rhs[0] += self.Du * u.laplace(self.bc)
        if self.Dv is not None:
            rhs[1] += self.Dv * v.laplace(self.bc)

        return rhs

    def solvetx(self):
        """simulate reaction diffusion system
        
        the simulation time is determined by shape of predetermined perturbation array

        Returns
        --------
        arrtx : `numpy.ndarray`, (T,X), float
            u level during simulation time at every grid point

        """
        '''
        
        '''
        memory = MemoryStorage()
        state = self.get_initial_state()#initial state
        self.solve(state, t_range=self.T, tracker=memory.tracker(1))
        arrtx = (np.stack(memory.data[1:],1)[0]).astype(np.float32)
        return arrtx



