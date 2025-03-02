#!/usr/bin/env python
"""
Compute the Canadian Forest Fire Weather Index (FWI) from daily meteorological inputs.
The formulas are based on Van Wagner (1987) and subsequent refinements.
Note: This implementation assumes that:
    - Temperature is provided in °C.
    - Relative Humidity is in %.
    - Wind speed is provided in km/h.
    - Precipitation is in mm.
The system is recursive, so previous day values for FFMC, DMC, and DC must be supplied.
"""

import numpy as np
import xarray as xr

def calc_ffmc(T, RH, wind, rain, ffmc_yesterday):
    """
    Calculate the Fine Fuel Moisture Code (FFMC).
    
    Parameters:
      T : xarray.DataArray or np.array
          Daily air temperature in °C.
      RH : xarray.DataArray or np.array
          Daily relative humidity in %.
      wind : xarray.DataArray or np.array
          Daily wind speed in km/h.
      rain : xarray.DataArray or np.array
          Daily precipitation in mm.
      ffmc_yesterday : xarray.DataArray or np.array
          Yesterday's FFMC (unitless, typically initialized around 85).
          
    Returns:
      ffmc : xarray.DataArray or np.array
          Today's FFMC.
    """
    # Convert previous FFMC to moisture content (m_o)
    m_o = 147.2 * (101.0 - ffmc_yesterday) / (59.5 + ffmc_yesterday)
    
    # Rainfall effect: only effective if rain > 0.5 mm
    # Effective rainfall (rf)
    rf = xr.where(rain > 0.5, rain - 0.5, 0.0)
    
    # Update moisture content after rain (m_r)
    # The following equations adjust m_o by the rain effect.
    # There are two regimes depending on whether m_o is below or above 150.
    m_r = xr.where(
        rf > 0,
        xr.where(m_o <= 150.0,
                 m_o + 42.5 * rf * np.exp(-100.0 / (251.0 - m_o)) * (1 - np.exp(-6.93 / rf)),
                 m_o + 42.5 * rf * np.exp(-100.0 / (251.0 - m_o)) * (1 - np.exp(-6.93 / rf)) + 0.0015 * (m_o - 150.0)**2 * np.sqrt(rf)
                ),
        m_o
    )
    # Cap moisture content at 250
    m_r = xr.where(m_r > 250.0, 250.0, m_r)
    
    # Equilibrium moisture content for drying (E_d) and wetting (E_w)
    E_d = 0.942 * (RH**0.679) + 11.0 * np.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - T) * (1 - np.exp(-0.115 * RH))
    E_w = 0.618 * (RH**0.753) + 10.0 * np.exp((RH - 100.0) / 10.0) + 0.18 * (21.1 - T) * (1 - np.exp(-0.115 * RH))
    
    # Drying or wetting phase: if m_r > E_d, drying; if m_r < E_w, wetting; otherwise, no change.
    # Calculate log drying and wetting rates:
    k_d = (0.424 * (1 - (RH / 100.0)**1.7) + 0.0694 * np.sqrt(wind) * (1 - (RH / 100.0)**8)) * 0.581 * np.exp(0.0365 * T)
    k_w = (0.424 * (1 - ((100.0 - RH) / 100.0)**1.7) + 0.0694 * np.sqrt(wind) * (1 - ((100.0 - RH) / 100.0)**8)) * 0.581 * np.exp(0.0365 * T)
    
    m = xr.where(m_r > E_d, E_d + (m_r - E_d) / (10**k_d),
         xr.where(m_r < E_w, E_w - (E_w - m_r) / (10**k_w),
                  m_r))
    
    # Convert moisture content back to FFMC
    ffmc = (59.5 * (250.0 - m)) / (147.2 + m)
    ffmc = xr.where(ffmc > 101.0, 101.0, ffmc)
    ffmc = xr.where(ffmc < 0.0, 0.0, ffmc)
    return ffmc

def calc_dmc(T, RH, rain, dmc_yesterday):
    """
    Calculate the Duff Moisture Code (DMC).
    
    Parameters:
      T : xarray.DataArray or np.array
          Daily air temperature in °C.
      RH : xarray.DataArray or np.array
          Daily relative humidity in %.
      rain : xarray.DataArray or np.array
          Daily precipitation in mm.
      dmc_yesterday : xarray.DataArray or np.array
          Yesterday's DMC.
          
    Returns:
      dmc : xarray.DataArray or np.array
          Today's DMC.
    """
    # Effective rainfall for DMC (in mm); threshold of 1.5 mm.
    rf = xr.where(rain > 1.5, rain, 0.0)
    # Rain effect: update DMC due to rain (Re)
    Re = 0.92 * rf - 1.27 if rf > 1.5 else 0.0  # Note: vectorize below
    Re = xr.where(rain > 1.5, 0.92 * rain - 1.27, 0.0)
    
    # Calculate adjustment term for DMC (based on temperature and RH)
    # Following Van Wagner (1987), use:
    # K = 1.894 * (T + 1.1) * (100 - RH) * 0.0001
    K = 1.894 * (T + 1.1) * (100 - RH) * 1e-4
    # DMC increases by rain-adjusted term plus the drying term K.
    dmc = xr.maximum(dmc_yesterday + Re + K, 0)
    return dmc

def calc_dc(T, rain, dc_yesterday):
    """
    Calculate the Drought Code (DC).
    
    Parameters:
      T : xarray.DataArray or np.array
          Daily air temperature in °C.
      rain : xarray.DataArray or np.array
          Daily precipitation in mm.
      dc_yesterday : xarray.DataArray or np.array
          Yesterday's DC.
          
    Returns:
      dc : xarray.DataArray or np.array
          Today's DC.
    """
    # Effective rainfall for DC: only if rain > 2.8 mm.
    rf = xr.where(rain > 2.8, rain, 0.0)
    Rd = xr.where(rain > 2.8, 0.83 * rain - 1.27, 0.0)
    # Potential evapotranspiration term: V = 0.36*(T+2.8) if T>= -2.8, else 0.
    V = xr.where(T >= -2.8, 0.36 * (T + 2.8), 0.0)
    dc = dc_yesterday + 0.5 * V
    # Adjust for rain: if rain > 2.8, update DC based on Rd.
    # Following Van Wagner (1987): Qo = 800 * exp(-dc_yesterday/400)
    Qo = 800 * np.exp(-dc_yesterday / 400.0)
    Qr = Qo + 3.937 * Rd
    Dr = 400 * np.log(800.0 / Qr)
    dc = xr.where(rain > 2.8, Dr, dc)
    dc = xr.maximum(dc, 0)
    return dc

def calc_isi(ffmc, wind):
    """
    Calculate the Initial Spread Index (ISI) based on FFMC and wind.
    
    Parameters:
      ffmc : xarray.DataArray or np.array
          Today's FFMC.
      wind : xarray.DataArray or np.array
          Wind speed in km/h.
          
    Returns:
      isi : xarray.DataArray or np.array
          Initial Spread Index.
    """
    # Convert FFMC to fine fuel moisture content (m)
    m = 250.0 - (ffmc * (147.2 + ffmc)) / 59.5
    # Fine fuel moisture function:
    f_F = 91.9 * np.exp(-0.1386 * m) * (1 + (m**5.31) / 4.93e7)
    # Wind function: f(W) = exp(0.05039 * wind)
    f_W = np.exp(0.05039 * wind)
    isi = 0.208 * f_W * f_F
    return isi

def calc_bui(dmc, dc):
    """
    Calculate the Buildup Index (BUI) from DMC and DC.
    
    Parameters:
      dmc : xarray.DataArray or np.array
          Duff Moisture Code.
      dc : xarray.DataArray or np.array
          Drought Code.
          
    Returns:
      bui : xarray.DataArray or np.array
          Buildup Index.
    """
    bui = xr.zeros_like(dmc)
    cond = dmc <= 0.4 * dc
    bui = xr.where(cond, (0.8 * dmc * dc) / (dmc + 0.4 * dc),
                     dmc - (1 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + 0.0114 * dmc))
    bui = xr.maximum(bui, 0)
    return bui

def calc_fwi(isi, bui):
    """
    Calculate the final Fire Weather Index (FWI) from ISI and BUI.
    
    Parameters:
      isi : xarray.DataArray or np.array
          Initial Spread Index.
      bui : xarray.DataArray or np.array
          Buildup Index.
          
    Returns:
      fwi : xarray.DataArray or np.array
          Fire Weather Index.
    """
    # First, compute an intermediate fire intensity index, B:
    # f(D) is defined piecewise:
    f_D = xr.where(bui <= 80, 0.626 * (bui ** 0.809) + 2,
                   1000.0 / (25.0 + 108.64 * np.exp(-0.023 * bui)))
    B = 0.1 * isi * f_D
    # Then, final FWI:
    fwi = xr.where(B > 1, np.exp(2.72 * ((0.434 * np.log(B)) ** 0.647)),
                   B)
    return fwi

def compute_fwi(dataset, ffmc_yesterday, dmc_yesterday, dc_yesterday):
    """
    Compute the full suite of FWI components given a dataset with the necessary variables.
    
    Parameters:
      dataset : xarray.Dataset
          Must contain variables: 't2m' (°C), 'RH' (%), 'windspeed' (km/h), and 'rain' (mm).
      ffmc_yesterday, dmc_yesterday, dc_yesterday:
          xarray.DataArray or np.array with yesterday's indices (initial conditions).
    
    Returns:
      updated_ds : xarray.Dataset
          Original dataset with added variables: 'FFMC', 'DMC', 'DC', 'ISI', 'BUI', and 'FWI'.
    """
    T = dataset['t2m_C']
    RH = dataset['RH']
    wind = dataset['windspeed']
    rain = dataset['tp']
    
    FFMC = calc_ffmc(T, RH, wind, rain, ffmc_yesterday)
    DMC = calc_dmc(T, RH, rain, dmc_yesterday)
    DC  = calc_dc(T, rain, dc_yesterday)
    ISI = calc_isi(FFMC, wind)
    BUI = calc_bui(DMC, DC)
    FWI = calc_fwi(ISI, BUI)
    
    updated_ds = dataset.copy()
    updated_ds['FFMC'] = FFMC
    updated_ds['DMC'] = DMC
    updated_ds['DC']  = DC
    updated_ds['ISI'] = ISI
    updated_ds['BUI'] = BUI
    updated_ds['FWI'] = FWI
    return updated_ds


