import numpy as np
from pde import PDEBase,MemoryStorage
class SRD(PDEBase):
    r'''
    solve two-variable reaction diffusion equations on 1d grid

    .. math::
 
        \frac{\partial u_{(x,t)}}{\partial t} = D_{u} \cdot \frac{\partial^2 u_{(x,t)}}{\partial x^2}+f_{u}(u_{(x,t)},v_{(x,t)})+\xi_{(x,t)}\\
        \frac{\partial v_{(x,t)}}{\partial t} = D_{v} \cdot \frac{\partial^2 v_{(x,t)}}{\partial x^2}+f_{v}(u_{(x,t)},v_{(x,t)})
    '''

    def __init__(self, arr, ode=None, DuDv=(None,None)):
        '''
        initialize noise interpolator, reaction ode, diffusion rate, boundary conditions
        '''

        self.T, self.gridsize = arr.shape
        from scipy.interpolate import RegularGridInterpolator as interp
        self.perturb = interp((np.arange(self.T), np.arange(self.gridsize)), arr, method='nearest', bounds_error=False, fill_value=0)

        self.ode = ode
        self.Du, self.Dv = DuDv # u,v diffusion rate
        self.bc = "natural" # boundary condition: vanishing derivative for non-periodic axis

        self.u0v0 = ode.roots()[0]#first fixed point
        
    def get_initial_state(self):
        '''
        initialize spatial grid
        '''
        from pde import UnitGrid, ScalarField, FieldCollection
        return FieldCollection([ScalarField(UnitGrid(self.gridsize,periodic=True), w) for w in self.u0v0])

    def evolution_rate(self, state, t=0):
        '''
        calculate changes in u,v level from perturb, react, diffuse
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
        '''
        calculate how concentraction changes over time
        '''
        memory = MemoryStorage()
        state = self.get_initial_state()#initial state
        self.solve(state, t_range=self.T, tracker=memory.tracker(1))
        arrtx = (np.stack(memory.data[1:],1)[0]).astype(np.float32)
        return arrtx



