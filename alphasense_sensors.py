# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:39:50 2022

@author: maruzka
"""

import pickle as pi
import dados_correcao_temp as dados_temp
import dados_alphasense as dados_sens

import functools

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug

class Alphasense_Sensors:
    
    fn_data = 'alphasense_sensor_data.pickle'

    def __init__(self, sensor_model, sensor_num):
        
        self.__sensor_num = sensor_num
        self.__sensor_model = sensor_model
       
        self.bt, self.gain, self.we_zero, self.ae_zero, \
        self.we_sensor, self.sensitivity, self.electronic_we,  \
        self.electronic_ae, self.no2_sensitivity = \
        self.__get_sensor_data(sensor_model, sensor_num)
        
        self.corrected_we, self.temp_correction_coef = self.__temperature_correction_func()
        
        
    def __temperature_correction_func(self):
        
        if self.__sensor_model == "SO2-B4":
           return self.__algorithm_4, dados_temp.ajuste_temp[self.__sensor_model]
        else:
            return self.__algorithm_1, dados_temp.ajuste_temp[self.__sensor_model]

    def __aux(self):
        
        if self.__sensor_model == "CO-B4" or self.__sensor_model == "H2S-B4":
            self.func_aux_wec = self.__algorithm_2
            # self.func_aux_wec.corr_temp = dados_temp.ajuste_temp[self.__sensor_model][1]

        else: 
            self.func_aux_wec = self.__algorithm_3
            # self.func_aux_wec.corr_temp = dados_temp.ajuste_temp[self.__sensor_model][2]

        
        
    def get_sensorType(self):
        return self.__sensor_type
    
    def get_sensorNumber(self):
        return self.__sensor_number
    
    def __get_sensor_data(self, sensor_model, sensor_num):
        
        with open(self.fn_data, "rb") as f:
            # data = pi.load(f)
            data = dados_sens.data[sensor_model][sensor_num]
            
        return data.values()
            
    def __algorithm_1(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[0][temp // 10 + 3]
        #print("kt", kt)

        # kt = dados_temp.ajuste_temp[self.__sensor_model][3]
        return (raw_we - self.electronic_we) - kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_2(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[1][temp // 10 + 3]
        #print("kt", kt)

        return (raw_we - self.electronic_we) - \
        (self.we_zero / self.ae_zero)*kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_3(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[2][temp // 10 + 3]
        # print("kt", kt)

        return (raw_we - self.electronic_we) - (self.we_zero - self.ae_zero) \
               - kt*(raw_ae - self.electronic_ae)
               
    def __algorithm_4(self, raw_we, raw_ae, temp):
        kt = self.temp_correction_coef[3][temp // 10 + 3]
        #print("kt", kt)
        return (raw_we - self.electronic_we) - self.we_zero - kt
    @debug
    def all_algorithms(self, raw_we, raw_ae, temp):
        return (self.__algorithm_1(raw_we, raw_ae, temp), \
                self.__algorithm_2(raw_we, raw_ae, temp), \
                self.__algorithm_3(raw_we, raw_ae, temp), \
                self.__algorithm_4(raw_we, raw_ae, temp))
    
    def sensor_configuration(self):
        
        print("Model:", self.__sensor_model)
        print("Sensor Number:", self.__sensor_num)
        print("Board Type:", self.bt)
        print("Primary Algorithm:", self.corrected_we.__name__)
        # print("Secondary Algorithm:", self.func_aux_wec.__name__)
        print("Gain:", self.gain, "[mV/nA]")
        print("Sensitivity:", self.sensitivity, "[mV/ppb]")
        print("-----------Working Electrode-----------")
        print("Electronic WE:", self.electronic_we, "[mV]")
        print("WE Zero:", self.we_zero, "[mV]")
        print("WE sensor:", self.we_sensor, "[nA/ppm]")
        print("-----------Aux Electrode-----------")
        print("Electronic AE:", self.electronic_ae, "[mV]")
        print("AE Zero:", self.ae_zero, "[mV]")
    
    def temperature_corr(self):
        print(self.corrected_we.hehehe)
        
    def PPB(self, raw_we, raw_ae, temp, algorithm = "suggested"):
        if algorithm == "suggested":
            return self.corrected_we(raw_we = raw_we, raw_ae = raw_ae, temp=temp) / self.sensitivity
        else:
            pass
            # return self.func_aux_wec(raw_we = raw_we, raw_ae = raw_ae, temp=0) / self.sensitivity
def main():
    
    fn_alpha_s = 'alphasense_sensor_data.pickle'
    
    co = Alphasense_Sensors("CO-B4", "162741357")
    co.sensor_configuration();
    print("")
    
    # h2s = Alphasense_Sensors("H2S-B4", "163740262")
    # h2s.sensor_configuration();
    # print("")

    # no2 = Alphasense_Sensors("NO2-B43F", "202742056")
    # no2.sensor_configuration();
    # print("")

    # so2 = Alphasense_Sensors("SO2-B4", "164240347")
    # so2.sensor_configuration();
    # print("")

    # ox = Alphasense_Sensors("OX-B431", "204240457")
    # ox.sensor_configuration();
    # print("")

    
    import matplotlib.pyplot as plt
    import numpy as np
    
    we = np.arange(0, 5000, 250)
    ae = np.arange(0, 5000, 250)
    
    we, ae = np.meshgrid(we, ae, sparse = False)

    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import matplotlib.colors as colors
    from matplotlib.ticker import LinearLocator, FormatStrFormatter
    import numpy as np
    import matplotlib.colors as colors
    import matplotlib.cbook as cbook
    from matplotlib import cm
    
    
    # fig = plt.figure()
    # ax = fig.gca(projection='3d')
    
    # Make data.

    temp = 20
    Z1, Z2, Z3, Z4 = co.all_algorithms(we, ae, temp)
    
    # Plot the surface.
    # surf = ax.plot_wireframe(we, ae, Z1,"b*", rstride=10, cstride=10, color = "b",
    #                          linewidth=2, antialiased=False, label = "Z1")
    # surf = ax.plot_wireframe(we, ae, Z2,rstride=10, cstride=10, color = "g",
    #                          linewidth=2, antialiased=False, label = "Z2")
    # surf = ax.plot_wireframe(we, ae, Z3,rstride=10, cstride=10, color = "r",
    #                    linewidth=2, antialiased=False, label = "Z3")
    # surf = ax.plot_wireframe(we, ae, Z4,rstride=10, cstride=10, color = "gray",
    #                    linewidth=2, antialiased=False, label = "Z4")
    
    # ax.plot_surface(we, ae, np.zeros(shape = we.shape), color = "gray", alpha = 0.5)
    
    X = we
    Y = ae
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig, ax = plt.subplots()
    
    CS = ax.contour(X, Y, Z4, 15, colors='k')  # Negative contours default to dashed.
    ax.clabel(CS, fontsize=9, inline=True)
    
    L = ax.axvline(x=co.we_zero + co.electronic_we + 50, color='g', linestyle=':', linewidth=2, label = "WE Zero")
    # ax.clabel(L, fontsize = 9, inline = True)
    
    ax.set_title('Algoritmo 4 - PPB > 0 VWE > Velectronic + Vzero + kt')
    ax.set_xlabel("Working Electrode")
    ax.set_ylabel("Auxiliary Electrode")
    
    fig, ax = plt.subplots()
    
    CS = ax.contour(X, Y, Z1, 15, colors='k')  # Negative contours default to dashed.
    ax.clabel(CS, fontsize=9, inline=True)
    
    L = ax.axvline(x=co.we_zero + co.electronic_we + 50, color='g', linestyle=':', linewidth=2, label = "WE Zero")
    # ax.clabel(L, fontsize = 9, inline = True)
    
    ax.set_title('Algoritmo 1 - PPB > 0 VWE > Velectronic + Vzero + kt')
    ax.set_xlabel("Working Electrode")
    ax.set_ylabel("Auxiliary Electrode")
    
    
            
        
  
if __name__ == "__main__":
    main()
        
        
