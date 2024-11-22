# Calculate the Reflectance based on Scattering and Absorption
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Pigment mappings
pigment_mapping = {
    'White': 'white',
    'Black': 'black',
    'Cobalt Blue': 'cobalt b',
    'Quinacridone Magenta': 'quinacridone Magenta',
    'Phthalo Blue (Green Shade)': 'phthalo blue (green shade)',
    'Hansa Yellow': 'hansa Yellow',
    'Phthalo Green': 'phthalo Green',
    'Pyrrole Red': 'pyrrole Red',
    'Ultramarine Blue': 'ultramarine Blue',
    'Dioxazine Purple': 'dioxazine Purple',
    'Pyrrole Orange': 'pyrrole Orange'
}

# Load data
data = pd.read_csv('data/prepared_data.csv')
wavelengths = data['wavelength'].values

# Equal wavelength intervals
delta_lambda = wavelengths[1] - wavelengths[0]

def gamma_correct(c):
    return pow(np.clip(c, 0, 1), 1 / 2.2)

# Function to convert XYZ to sRGB
def xyz_to_srgb(X, Y, Z):
    # sRGB conversion matrix
    M = np.array([[3.2406, -1.5372, -0.4986],
                  [-0.9689,  1.8758,  0.0415],
                  [0.0557, -0.2040,  1.0570]])
    
    # Convert XYZ to linear RGB
    RGB_lin = np.dot(M, [X, Y, Z])

    # Gamma correction
    RGB = [gamma_correct(c) for c in RGB_lin]

    return np.clip(RGB, 0, 1)

# Function to compute sRGB from a mixture of pigments
def compute_mixture_srgb(pigment_names, proportions):
    # Ensure proportions sum to 1
    proportions = np.array(proportions)
    proportions = proportions / proportions.sum()

    # Initialize K_mix and S_mix as float arrays
    K_mix = np.zeros_like(data['wavelength'].values, dtype=float)
    S_mix = np.zeros_like(data['wavelength'].values, dtype=float)

    # Sum K and S values weighted by proportions
    for pigment_name, proportion in zip(pigment_names, proportions):
        pigment_key = pigment_mapping[pigment_name]
        K = data['k ' + pigment_key].values
        S = data['s ' + pigment_key].values
        K_mix += proportion * K
        S_mix += proportion * S

    # Compute K/S ratio
    ks_ratio = K_mix / S_mix

    # Compute reflectance R(λ) using Kubelka-Munk theory
    Q = np.sqrt(ks_ratio * (ks_ratio + 2))
    R_inf = 1 + ks_ratio - Q
    R_inf = np.clip(R_inf, 0, 1)
    
    # Extract color matching functions and illuminant data
    x_bar = data['x_bar'].values
    y_bar = data['y_bar'].values
    z_bar = data['z_bar'].values
    I = data['power'].values

    # Compute the XYZ tristimulus values
    X_num = np.sum(R_inf * I * x_bar) * delta_lambda
    Y_num = np.sum(R_inf * I * y_bar) * delta_lambda
    Z_num = np.sum(R_inf * I * z_bar) * delta_lambda

    # Normalization factor
    Y_norm = np.sum(I * y_bar) * delta_lambda

    # Normalize XYZ values
    X = X_num / Y_norm
    Y = Y_num / Y_norm
    Z = Z_num / Y_norm

    # Convert to sRGB
    sRGB = xyz_to_srgb(X, Y, Z)

    return sRGB

# Function to generate mixtures and plot the color gamut
def plot_color_gamut(pigment_names):
    # Generate all combinations of proportions that sum to 1
    resolution = 21  # Adjust for finer granularity
    num_pigments = len(pigment_names)

    if num_pigments == 2:
        fractions = np.linspace(0, 1, resolution)
        sRGB_list = []

        for f in fractions:
            proportions = [f, 1 - f]
            sRGB = compute_mixture_srgb(pigment_names, proportions)
            sRGB_list.append(sRGB)

        # Plot the colors
        plt.figure(figsize=(12, 2))
        color_array = np.array([sRGB_list])
        plt.imshow(color_array, extent=[0, 1, 0, 0.1])
        plt.xlabel(f'Fraction of {pigment_names[0]}')
        plt.yticks([])
        plt.xticks(fractions, [f"{f:.2f}" for f in fractions], rotation=45)
        plt.title(f"Color Gamut of Mixture: {pigment_names[0]} and {pigment_names[1]}")
        plt.show()

    elif num_pigments == 3:
        # Create a triangular grid of proportions
        ternary_points = []
        sRGB_list = []

        for i in range(resolution):
            for j in range(resolution - i):
                k = resolution - i - j - 1
                proportions = [i / (resolution - 1), j / (resolution - 1), k / (resolution - 1)]
                sRGB = compute_mixture_srgb(pigment_names, proportions)
                ternary_points.append(proportions)
                sRGB_list.append(sRGB)

        # Prepare data for plotting
        ternary_points = np.array(ternary_points)
        sRGB_list = np.array(sRGB_list)

        # Plotting the color gamut in 2D
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

        # Convert ternary coordinates to Cartesian for plotting
        x_coords = 0.5 * (2 * ternary_points[:, 1] + ternary_points[:, 2]) / (ternary_points.sum(axis=1))
        y_coords = (np.sqrt(3) / 2) * ternary_points[:, 2] / (ternary_points.sum(axis=1))

        ax.scatter(x_coords, y_coords, c=sRGB_list, s=50)

        # Set labels and titles
        ax.set_xlabel(f'{pigment_names[1]}')
        ax.set_ylabel(f'{pigment_names[2]}')
        plt.title(f"Color Gamut of Mixture: {', '.join(pigment_names)}")
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()

    else:
        print("Mixing more than 3 pigments is complex to visualize. Please select up to 3 pigments.")

# Example usage:

# Mix two pigments with better gamut representation
pigment_names = ['Cobalt Blue', 'Hansa Yellow']
plot_color_gamut(pigment_names)

# Mix three pigments
pigment_names = ['Cobalt Blue', 'Hansa Yellow', 'Pyrrole Red']
plot_color_gamut(pigment_names)
