import pandas as pd
from pathlib import Path
import ipywidgets as widgets
from autumn.projects.sm_covid2.common_school.output_plots import country_highlight as ch

from autumn.projects.sm_covid2.common_school.runner_tools import INCLUDED_COUNTRIES

analysis_names = {
    "main": "Base case analysis",
    "increased_hh_contacts": "SA1: Increased household transmission during closures",
    "no_google_mobility": "SA2: Without Google mobility data"
}

def get_analysis_widgets():
    dropdown_countries = [(c, iso3) for iso3, c in INCLUDED_COUNTRIES['all'].items()]
    iso3_widget = widgets.Dropdown(
        options=dropdown_countries,
        value="AUS",
        description='Country:',
    )
    analysis_widget = widgets.Dropdown(
        options=[(b, a) for a, b in analysis_names.items()],
        value="main",
        description='Analysis:',
    )

    return iso3_widget, analysis_widget


def get_derived_output_widget():
    return widgets.Dropdown(
        options=['cumulative_incidence', 'cumulative_incidenceXstrain_delta',
       'cumulative_incidenceXstrain_omicron',
       'cumulative_incidenceXstrain_wild_type',
       'cumulative_incidence_propXstrain_delta',
       'cumulative_incidence_propXstrain_omicron',
       'cumulative_incidence_propXstrain_wild_type',
       'cumulative_infection_deaths', 'elderly_incidence_prop',
       'ever_infected', 'hospital_admissions', 'hospital_occupancy',
       'incidence', 'incidenceXagegroup_0', 'incidenceXagegroup_15',
       'incidenceXagegroup_25', 'incidenceXagegroup_50',
       'incidenceXagegroup_70', 'infection_deaths', 'infection_deaths_ma7',
       'n_immune_unvaccinated', 'n_immune_vaccinated',
       'peak_hospital_occupancy', 'prop_ever_infected',
       'prop_ever_infected_age_matched', 'prop_immune_unvaccinated',
       'prop_immune_vaccinated',
       'total_population', 'transformed_random_process'
        ],
        value="incidence",
        description='Output:',
    )



def load_analysis_outputs(iso3, analysis):    
    folder_path = Path.cwd() / analysis / iso3

    uncertainty_dfs = {sc: pd.read_parquet(folder_path/ f"uncertainty_df_{sc}.parquet") for sc in ["baseline", "scenario_1"]}
    diff_quantiles_df = pd.read_parquet(folder_path / f"diff_quantiles_df.parquet")
    derived_outputs = pd.read_pickle(folder_path / "derived_outputs.pickle") 

    return uncertainty_dfs, diff_quantiles_df, derived_outputs


def get_diff_quantiles_table(diff_quantiles_df):
    f_diff_quantiles_df = - diff_quantiles_df[
        ['cases_averted', 'cases_averted_relative', 'delta_hospital_peak_relative', 'deaths_averted', 'deaths_averted_relative']
    ] # use "-" so positive nbs indicate positive effect of closures

    for col in f_diff_quantiles_df.columns:
        if col.endswith("_relative"):
            f_diff_quantiles_df[col] = round(100. * f_diff_quantiles_df[col], 1)
        else:
            f_diff_quantiles_df[col] = (round(f_diff_quantiles_df[col])).astype("int")

    # rename columns
    rename_map = {
        "cases_averted": "N infections averted",
        "cases_averted_relative": "% infections averted",
        "deaths_averted": "N deaths averted",
        "deaths_averted_relative": "% deaths averted",
        # "delta_hospital_peak": "Hospital peak reduction",
        "delta_hospital_peak_relative": "% hospital peak reduction"
    }
    f_diff_quantiles_df.rename(mapper=rename_map, inplace=True, axis=1)

    # rename and reorder quantile index
    f_diff_quantiles_df.rename(index=lambda q: f"{round(100. * (1. - q), 1)}%" ,inplace=True)
    f_diff_quantiles_df.index.name = "percentile"
    f_diff_quantiles_df = f_diff_quantiles_df.iloc[::-1]

    return f_diff_quantiles_df


sc_names = {"baseline": "Historical", "scenario_1": "Counterfactual (schools open)"}

def plot_derived_outputs(derived_outputs, output, iso3, analysis):    
    df = pd.DataFrame({sc_names[sc]: derived_outputs[sc][output] for sc in derived_outputs})
    ax = df.plot(labels={"value": output,"variable": "Scenario"}, title=f"{INCLUDED_COUNTRIES['all'][iso3]} - {analysis_names[analysis]}")
    ax.show()

def plot_uncertainty(uncertainty_dfs, output, iso3, analysis):

    for sc in uncertainty_dfs:
        f = uncertainty_dfs[sc][output].plot(labels={"value": output}, title= f"{INCLUDED_COUNTRIES['all'][iso3]} - {analysis_names[analysis]} <br> {sc_names[sc]} scenario")
        f.show()