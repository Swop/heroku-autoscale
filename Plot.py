#from numpy import *
import Gnuplot

class Plot(object):

    @staticmethod
    def plot(checks, rep_time_avg, rep_time_trend, response_time_low, response_time_high, file="out.png", terminal="png"):
        times = checks.keys()
        times.sort()
        
        checks_count = len(times)
        
        values = []
        for time in times:
            values.append(checks[time].get_response_time())
            
        first_time = times[0]
        
        plot_times = [(x - first_time)/60 for x in times]
        
        d = Gnuplot.Data(plot_times, values)
        d2 = Gnuplot.Data(plot_times, [rep_time_avg]*checks_count)
        d3 = Gnuplot.Data(plot_times, [response_time_low]*checks_count)
        d4 = Gnuplot.Data(plot_times, [response_time_high]*checks_count)

        g = Gnuplot.Gnuplot()
        g('set style data lines')
        
        g.plot(d, d2, d3, d4)
        g.hardcopy(filename=file,terminal=terminal)