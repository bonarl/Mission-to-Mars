def gravity_turn(deltav,pitchover_angle,tf):
    pitchover_angle = pitchover_angle*np.pi/180
    def sys_dynamics(t,X): 
    #state vector X, function returns dX/dt for given X = [v,y,r,th,m]
        #v, velocity 
        #y, angle between velocity and local vertical
        #r&th, Earth centred polar coordinates 
        #m, mass
        v,y,r,th,m=X[0:6]
        if m>m_dry: #if fuel left, decrease mass
            md = -ttw*m/(ISP)
            emptyflag = 1.0
        else:
            md=0.0
            emptyflag = 0.0
        #acceleration = thrust-gravity-drag (zero angle-of-attack)
        vd = emptyflag*ttw*(M_earth*G/r**2) - (M_earth*G/r**2)*np.cos(y)-1*(0.5*rho(r)*Cd*A*v**2)/m   
        #polar coord. velocities
        rd = v*np.cos(y)
        thd = (v*np.sin(y))/r
        #rotation rate, exception for singularity at v=0
        if v != 0:
            yd = (M_earth*G/r**2)/v*np.sin(y)-thd
        else: 
            yd = 0.0
        return [vd,yd,rd,thd,md]
    def hit_ground(t, y): return y[2]-6369e3
    hit_ground.terminal = True
    hit_ground.direction = -1
    def nofuel(t, y): return y[4]-m_dry
    nofuel.terminal = True
    nofuel.direction = -1
    def apex(t,y):return np.pi/2-y[1]
    apex.terminal = True
    apex.direction = -1
    #initial conditions
    X0=[252,pitchover_angle,6371.0e3,0.0,m_wet]
    #solving and unpacking
    sol = solve_ivp(sys_dynamics,[0, tf],X0,method='BDF',t_eval = np.linspace(0,tf,int(tf)), events=[hit_ground])
    ys = sol.y[1,:]
    rs = sol.y[2,:]
    ths = sol.y[3,:]
    ms = sol.y[4,:]
    ts = sol.t
    xs=rs*np.sin(ths)
    ys=rs*np.cos(ths)
    #plotting
    f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)
    ax1.plot(xs,ys)
    ax2.plot(xs,ys)
    lim = 6370e3+2000e3
    ax1.set_xlim([-800e3,3000e3])
    ax1.set_ylim([6370e3-800e3,6370e3+1600e3])
    ax2.set_xlim([-lim,lim])
    ax2.set_ylim([-lim,lim])
    f.set_size_inches(20, 10, forward=True)
    earth1=patches.Circle([0,0],6370e3)
    draw_circle1 = plt.Circle((0, 0), 6370e3+800e3,fill=False,linestyle='--',edgecolor='r')
    earth2=patches.Circle([0,0],6370e3)
    draw_circle2 = plt.Circle((0, 0), 6370e3+800e3,fill=False,linestyle='--',edgecolor='r')
    ax1.add_patch(earth1)
    ax1.add_artist(draw_circle1)
    ax1.set_aspect('equal')
    ax2.add_patch(earth2)
    ax2.add_artist(draw_circle2)
    ax2.set_aspect('equal')
    plt.show()
    return sol
def animate_trajectory(sol):
    ys = sol.y[1,:]
    rs = sol.y[2,:]
    ths = sol.y[3,:]
    ms = sol.y[4,:]
    ts = sol.t
    #plt.plot(ts,rs)
    xs=rs*np.sin(ths)
    ys=rs*np.cos(ths)
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10, forward=True)
    lim = 20000e3
    ax.axis([-lim,lim,-lim,lim])
    earth=patches.Circle([0,0],6370e3)
    ax.add_patch(earth)
    ax.set_aspect('equal')
    earth=patches.Circle([0,0],6370e3)
    line, = ax.plot([], [],lw=2)
    point, = ax.plot(0,1, marker="o")
    def init():
        line.set_data([], [])
        return (line,)
    def animate(i):
        x = xs[0:1+i*100]
        y = ys[0:1+i*100]
        line.set_data(x, y)
        point.set_data(x[-1],y[-1])
        return (line,point,)
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=300, interval=50, blit=True)
    return HTML(anim.to_jshtml())