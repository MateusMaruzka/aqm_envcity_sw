# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:39:50 2022

@author: maruzka
"""

import pickle as pi
import dados_correcao_temp as dados_temp


# import functools

# def decorator(func):
#     @functools.wraps(func)
#     def wrapper_decorator(*args, **kwargs):
#         # Do something before
#         value = func(*args, **kwargs)
#         # Do something after
#         return value
#     return wrapper_decorator




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
           return self.__algorithm_4, dados_temp.ajuste_temp[self.__sensor_model][3]
        else:
            return self.__algorithm_1, dados_temp.ajuste_temp[self.__sensor_model][0]

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
            data = pi.load(f)
            data = data[sensor_model][sensor_num]
            
        return data.values()
            
    def __algorithm_1(self, raw_we, raw_ae, temp):
        kt = 1
        return (raw_we - self.electronic_we) - kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_2(self, raw_we, raw_ae, temp):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - \
        (self.we_zero / self.ae_zero)*kt*(raw_ae - self.electronic_ae)
    
    def __algorithm_3(self, raw_we, raw_ae, temp):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - (self.we_zero - self.ae_zero) \
               - kt*(raw_ae - self.electronic_ae)
               
    def __algorithm_4(self, raw_we, raw_ae, temp):
        kt = 1 # TODO
        return (raw_we - self.electronic_we) - self.we_zero - kt
    
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
        
    def PPB(self, raw_we, raw_ae, algorithm = "suggested"):
        if algorithm == "suggested":
            return self.corrected_we(raw_we = raw_we, raw_ae = raw_ae, temp=0) / self.sensitivity
        else:
            pass
            # return self.func_aux_wec(raw_we = raw_we, raw_ae = raw_ae, temp=0) / self.sensitivity

          
    
        
        
def main():
    
    fn_alpha_s = 'alphasense_sensor_data.pickle'
    
    co = Alphasense_Sensors("CO-B4", "162741357")
    co.sensor_configuration();
    print("")
    
    h2s = Alphasense_Sensors("H2S-B4", "163740262")
    h2s.sensor_configuration();
    print("")

    no2 = Alphasense_Sensors("NO2-B43F", "202742056")
    no2.sensor_configuration();
    print("")

    so2 = Alphasense_Sensors("SO2-B4", "164240347")
    so2.sensor_configuration();
    print("")

    ox = Alphasense_Sensors("OX-B431", "204240457")
    ox.sensor_configuration();
    print("")

    
    import matplotlib.pyplot as plt
    import numpy as np
    
    we = np.arange(0, 5000, 250)
    ae = np.arange(0, 5000, 250)
    
    we, ae = np.meshgrid(we, ae, sparse = True)

    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.ticker import LinearLocator, FormatStrFormatter
    import numpy as np
    
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    
    # Make data.

    Z = co.PPB(we, ae)
    # Plot the surface.
    surf = ax.plot_surface(we, ae, Z,rstride=1, cstride=1, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
    
    # ax = fig.add_subplot(1, 2, 2, projection='3d')

    # # plot a 3D wireframe like in the example mplot3d/wire3d_demo
    # ax.plot_wireframe(we, ae, Z, rstride=10, cstride=10)
    
    # plt.show()
if __name__ == "__main__":
    main()
        
        
