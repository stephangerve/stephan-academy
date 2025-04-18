import numpy as np
import matplotlib.pyplot as plt

def likelihood_function(theta, data):
    likelihood = 1.0
    for x in data:
        likelihood *= (1 / theta) if 0 <= x <= theta else 0
    return likelihood

if __name__ == "__main__":
    # Sample data points for illustration
    data_points = [1, 2, 3, 4, 5]

    # Range of theta values for the plot
    theta_values = np.linspace(0.1, 10, 1000)

    # Calculate likelihood values for each theta value
    likelihood_values = [likelihood_function(theta, data_points) for theta in theta_values]

    # Plot the likelihood function
    plt.plot(theta_values, likelihood_values)
    plt.xlabel('θ (Parameter)')
    plt.ylabel('Likelihood Function (log scale)')
    plt.yscale('log')
    plt.title('Likelihood Function for (1/θ) * I[0, θ](x)')
    plt.grid(True)
    plt.show()
