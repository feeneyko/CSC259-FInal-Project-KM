import os
import pandas as pd

cie_xyz = pd.read_csv(os.path.join('data', 'CIE_xyz_1931_2deg.csv'))
ks_data = pd.read_csv(os.path.join('data', 'k_and_s_Yoshi_data.csv'))
illuminant_d65 = pd.read_csv(os.path.join('data', 'CIE_std_illum_D65.csv'))
illuminant_d50 = pd.read_csv(os.path.join('data', 'CIE_std_illum_D50.csv'))
illuminant_a = pd.read_csv(os.path.join('data', 'CIE_std_illum_A_1nm.csv'))

data = pd.merge(ks_data, cie_xyz, on='wavelength', how='inner')
data = pd.merge(data, illuminant_d65, on='wavelength', how='inner')
data = pd.merge(data, illuminant_d50, on='wavelength', how='inner')
data = pd.merge(data, illuminant_a, on='wavelength', how='inner')

os.makedirs('data', exist_ok=True)

data.to_csv(os.path.join('data', 'prepared_data_3i.csv'), index=False)