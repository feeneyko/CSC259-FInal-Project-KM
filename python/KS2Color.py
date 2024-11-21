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
    return pow(c, 1 / 2.2)
# def gamma_correct(c):
#     if c <= 0.0031308:
#         return 12.92 * c
#     else:
#         return 1.055 * pow(c, 1/2.4) - 0.055

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

# Initialize plot
plt.figure(figsize=(12, 8))

# Loop through each pigment
for i, (pigment_name, pigment_key) in enumerate(pigment_mapping.items()):
    # Extract K and S data for the current pigment
    k_col = 'k ' + pigment_key
    s_col = 's ' + pigment_key

    K = data[k_col].values
    S = data[s_col].values

    # Compute K/S ratio
    ks_ratio = K / S

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

    # Display the sRGB values
    # print(f"sRGB values for {pigment_name}: {sRGB}")

    # Plot the color
    plt.subplot(3, 4, i + 1)
    plt.imshow([[(sRGB[0], sRGB[1], sRGB[2])]])
    plt.axis('off')
    plt.title(pigment_name)

plt.tight_layout()
plt.show()
