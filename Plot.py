import Gnuplot
from pingdom.pingdomcheck import PingdomCheck

class Plot(object):

    @staticmethod
    def plot(checks, rep_time_avg, reg_coef, response_time_low, response_time_high, file="out.ps", terminal="postscript"):
        x, y = PingdomCheck.getArrayData(checks)
        checks_count = len(x)
            
        reg_values = []
        for time in x:
            reg_values.append(reg_coef[0] * time + reg_coef[1])
            
        first_time = x[0]
        plot_times = [(time - first_time) for time in x]
        
        checks_graph = Gnuplot.Data(plot_times, y, title='Pingdom checks', with_='lines lc rgb "red" lw 2')
        average_graph = Gnuplot.Data(plot_times, [rep_time_avg]*checks_count, title='Avg. response time', with_='lines lc rgb "green" lw 1')
        resp_time_low_graph = Gnuplot.Data(plot_times, [response_time_low]*checks_count, title='Resp. time low bound', with_='lines lc rgb "grey" lw 1')
        resp_time_high_graph = Gnuplot.Data(plot_times, [response_time_high]*checks_count, title='Resp. time high bound', with_='lines lc rgb "grey" lw 1')
        lin_reg_graph = Gnuplot.Data(plot_times, reg_values, title='Resp. time tendency', with_='lines lc rgb "blue" lw 1')

        g = Gnuplot.Gnuplot()
        g.plot(checks_graph, average_graph, resp_time_low_graph, resp_time_high_graph, lin_reg_graph)
        
        g.xlabel('Time (s)')
        g.ylabel('Response time (ms)')
        g.replot()
        
        g.hardcopy(filename=file,terminal=terminal)