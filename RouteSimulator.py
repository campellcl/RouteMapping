"""
RouteSimulator.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class RouteSimulator:
    pass

def main(df_route, n, nb, E, W, Crr1, Crr2, N, P, Cd, A, Na, g, v):
    # Power in = power out
    # n*(nb*E + ((P*x)/v) = ((W*Crr1)+(N*Crr2*v)+((1/2)p*cD
    ''' Add columns to dataframe '''
    df_route['n'] = n
    df_route['nb'] = nb
    df_route['E'] = E
    df_route['W'] = W
    df_route['Crr1'] = Crr1
    df_route['Crr2'] = Crr2
    df_route['N'] = N
    df_route['P'] = P
    df_route['Cd'] = Cd
    df_route['A'] = A
    df_route['Na'] = Na
    df_route['g'] = g
    df_route['v'] = v
    # The first entry is not a number.
    power_out = [np.NaN]
    # Extract the change in elevation as a pd.Series object:
    delta_elv = df_route['Elv_diff'].data
    delta_dist = df_route['Vincenty_dist'].data
    for i, (elv, dist) in enumerate(zip(delta_elv, delta_dist)):
        if i != 0:
            # energy_req = (((W*Crr1)+((N*Crr2)*v)+((((.5*P)*Cd)*A)*(v**2)))*dist)+(W*elv)+(((Na*W)*(v**2))/(2*g))
            if dist != 0.0:
                energy_req = (((((W*Crr1)+((N*Crr2)*v)+((((.5*P)*Cd)*A)*(v**2)))*dist)+(W*elv))/dist)
            else:
                energy_req = 0.0
            # Convert Energy in Watt-Seconds (Joules) to KiloWatt-Hours:
            # energy_req = energy_req / 3600000
            # Convert Energy in Watt-Seconds to Watt-Hours:
            energy_req = energy_req / 3600
            power_out.append(energy_req)
    # The total watt hours (sum(power_out[1:])) divided by 1000 is kilowatt hours.
    df_route['Power_out'] = power_out
    # print(df_route[['Energy_out','Elv_diff','Vincenty_dist']])
    vin_dist = df_route['Vincenty_dist'].data[1:]
    accumulated_vincenty_dist = [0.0]
    for i, dist in enumerate(vin_dist):
        accumulated_vincenty_dist.append(accumulated_vincenty_dist[i]+dist)
    accumulated_power_out = [0.0]
    for i, output in enumerate(power_out[1:]):
        accumulated_power_out.append(accumulated_power_out[i]+output)
    '''
    plt.axis([min(accumulated_vincenty_dist),
              max(accumulated_vincenty_dist),
              min(df_route['Elv'].data[1:]),
              max(df_route['Elv'].data[1:])])
    '''
    plt.title('Elevation Profile')
    plt.xlabel('Total Vincenty Distance (meters)')
    plt.ylabel('Elevation (meters)')
    # plt.axis([0,30000,-60, 60])
    plt.plot(accumulated_vincenty_dist, df_route['Elv'].data)
    # plt.plot(accumulated_vincenty_dist, df_route['Power_out'])
    # plt.plot(accumulated_vincenty_dist, df_route['Energy_out'].data, 'r')
    plt.show()
    plt.clf()

    fig, ax1 = plt.subplots()
    ax1.plot(accumulated_vincenty_dist, df_route['Elv'])
    ax1.set_xlabel('Vincenty Distance (meters)')
    ax1.set_ylabel('Elevation (meters)', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(accumulated_vincenty_dist, df_route['Power_out'], 'g')
    ax2.set_ylabel('Power (kW)', color='g')
    ax2.tick_params('y', colors='g')
    plt.title('Elevation Profile & Net Power')
    plt.show()

    # Plot Accumulated total energy vs accumulated distance.
    plt.clf()
    fig, ax1 = plt.subplots()
    ax1.plot(accumulated_vincenty_dist, df_route['Elv'])
    ax1.set_xlabel('Vincenty Distance (meters)')
    ax1.set_ylabel('Elevation (meters)', color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(accumulated_vincenty_dist, accumulated_power_out, 'g')
    ax2.set_ylabel('Total Energy (kWh)', color='g')
    ax2.tick_params('y', colors='g')
    plt.title('Elevation Profile & Total Energy Consumption')
    plt.show()
    # TODO: Rewrite equation for power instead of energy.

if __name__ == '__main__':
    route = Path('df_route.pkl')
    if route.is_file():
        df_route = pd.read_pickle(str(route))
    else:
        print("Error: Route dataframe must be constructed prior to execution.")
        exit(-1)
    ''' Get user input '''
    print("Route Simulator v1.0. Please input the required parameters...")
    '''
    # Motor, controller and drive train efficiency (decimal):
    n = input("Motor, controller and drive train efficiency (decimal) [n]:")
    n = float(n)
    # Watt-hour battery efficiency (decimal):
    nb = input("Watt-hour battery efficiency (decimal) [n_b]:")
    nb = float(nb)
    # Energy available in the batteries (joules):
    E = input("Energy available in the batteries (joules) [E]:")
    E = float(E)
    # Weight of the vehicle including payload (newtons):
    W = input("Weight of the vehicle including payload (newtons) [W]:")
    W = float(W)
    # First coefficient of rolling resistance (non-dimensional):
    Crr1 = input("First coefficient of rolling resistance (non-dimensional) [C_rr1]:")
    Crr1 = float(Crr1)
    # Second coefficient of rolling resistance (newton-seconds per meter):
    Crr2 = input("Second coefficient of rolling resistance (newton-seconds per meter) [C_rr2]:")
    Crr2 = float(Crr2)
    # Number of wheels on the vehicle (integer):
    N = input("Number of wheels on the vehicle (integer) [N]:")
    N = int(N)
    # Air density (kilograms per cubic meter):
    P = input("Air density (kilograms per cubic meter) [P]:")
    P = float(P)
    # Coefficient of drag (non-dimensional):
    Cd = input("Coefficient of drag (non-dimensional) [C_d]:")
    Cd = float(Cd)
    # Frontal area (square meters):
    A = input("Frontal area (square meters) [A]:")
    A = float(A)
    # Number of times the vehicle will accelerate in a race day (integer):
    Na = input("Number of times the vehicle will accelerate in a race day (integer) [N_a]:")
    Na = int(Na)
    # Local acceleration due to gravity variable (meters per second squared):
    g = input("Local acceleration due to gravity variable (meters per second squared) [g]:")
    g = float(g)
    # Calculated average velocity over the route (meters per second):
    v = input("Calculated average velocity over the route (meters per second) [v]:")
    v = float(v)
    '''
    # Example Parameters:
    n = .95
    nb = 0.98
    E = 36000000.0
    W = 3900.0
    Crr1 = .0015
    Crr2 = 0.0
    N = 4
    P = 1.225
    Cd = .2
    A = .1
    Na = 1
    g = 9.8
    v = 16
    main(df_route=df_route,n=n,nb=nb,E=E,W=W,Crr1=Crr1,Crr2=Crr2,N=N,P=P,Cd=Cd,A=A,Na=Na,g=g,v=v)





