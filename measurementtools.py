"""
Some functions to compute data from Pingdom checks data
By Sylvain MAUDUIT (Swop)
"""

from pingdom.pingdomcheck import PingdomCheck

def getResponseTimeAvg(checks):
    """Return the average of the response times
    
    Arguments:
    - checks: A dictionary (key: check time) of pingdomcheck.PingdomCheck objects
    """
    x, y = PingdomCheck.getArrayData(checks)
    
    avg = 0
    for resp_time in y:
        avg += resp_time
    avg /= len(x)
    return avg

def computeLinearRegressionModel(checks):
    """Compute a linear regression model for experimental measures.
    
    The model is a function y' = ax + b which best fit the scatter plot of given experimental measures.
    
    Arguments:
    - x, y : vectors (lists) of measures
    
    Return: [a, b], the coefficient of the linear regression model
    """
    
    def sum_vector(n, x):
        sum = 0
        for i in range(n):
            sum += x[i]
        return sum
    
    def sum_vector_power(n, x, power):
        sum = 0
        for i in range(n):
            sum += pow(x[i], power)
        return sum
        
    def sum_xiyi(n, x, y):
        sum = 0
        for i in range(n):
            sum += x[i] * y[i]
        return sum
    
    x, y = PingdomCheck.getArrayData(checks)
    
    n = len(x)
    if(n != len(y)):
        raise Exception('You must have the same count of measures in x and y vectors.')
    
    a = float((n * sum_xiyi(n, x, y) - sum_vector(n, x) * sum_vector(n, y))) / float((n * sum_vector_power(n, x, 2) - pow(sum_vector(n, x), 2)))
    b = float((sum_vector(n, y) * sum_vector_power(n, x, 2) - sum_vector(n, x) * sum_xiyi(n, x, y))) / float((n * sum_vector_power(n, x, 2) - pow(sum_vector(n, x), 2)))
    
    return [a, b]