import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm.notebook import trange, tqdm
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo


def dashboard_html(outputs, filename):
    '''Saves a list of plotly figures in an html file.

    Parameters
    ----------
    figs : list[plotly.graph_objects.Figure]
        List of plotly figures to be saved.

    filename : str
        File name to save in.

    '''
    dashboard = open(filename, 'w')
    dashboard.write('<html><head>\
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">\
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap-theme.min.css" integrity="sha384-6pzBo3FDv/PJ8r2KRkGHifhEocL+1X2rVCTTkUfGk7/0pbek5mMa1upzvWbrUbOZ" crossorigin="anonymous">\
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>\
    </head><body>' + '\n')

    add_js = True
    dashboard.write('<div class="container">')
    for type, output in outputs:
        if type == 'fig':
            inner_html = pyo.plot(output, include_plotlyjs=add_js, output_type='div')
            dashboard.write('<div class="clearfix" style="height: 600px;">')
            dashboard.write(inner_html)
            dashboard.write('</div>')
            add_js = False
        elif type == 'table':
            dashboard.write('<div class="clearfix">')
            dashboard.write(
                output.to_html().replace('<table border="1" class="dataframe">','<table class="table table-striped">') # use bootstrap styling
            )
            dashboard.write('</div>')
        else:
            print(f'Unknown output type {type}.')
    dashboard.write('</div>')
    dashboard.write("</body></html>" + "\n")

local_smoothing_window_size = 5
avg_calculation_window_size = 800
frequency_calculation_window_size = 800
input_filename = r'D:\Hella\Hrabova_test_long_spatne_svetlo_128\Hrabova_test_long_spatne_svetlo_128_50_cut.parquet.gzip'
output_filename = r'D:\Hella\Hrabova_test_long_spatne_svetlo_128\analyse_signal_output_50.html'
print('Script for signal analysis started.')

figs = list()
df_avg = pd.read_parquet(input_filename, engine='pyarrow')

print(f'Data loaded from file {input_filename}.')

print('Processing signal..')
df_avg['smoothed_avg_edge_occurence'] = df_avg.rolling(local_smoothing_window_size, center=True).Edge_Avg.mean()
df_avg['rolling_avg_edge_occurence'] = df_avg.rolling(avg_calculation_window_size, center=True).Edge_Avg.mean()

df_avg.loc[df_avg.smoothed_avg_edge_occurence>=df_avg.rolling_avg_edge_occurence, 'polarity_smoothed'] = 1
df_avg.loc[df_avg.smoothed_avg_edge_occurence<df_avg.rolling_avg_edge_occurence, 'polarity_smoothed'] = -1
df_avg['polarity_smoothed_shift_abs'] = abs(df_avg.polarity_smoothed-df_avg.polarity_smoothed.shift())
df_avg['polarity_smoothed_shift'] = df_avg.polarity_smoothed-df_avg.polarity_smoothed.shift()

df_avg['frames_timediff_us'] = df_avg.FrameTimestamp_us - df_avg.FrameTimestamp_us.shift()
df_avg['periody_start_mark'] = 0
df_avg.loc[df_avg.polarity_smoothed_shift == 2, 'periody_start_mark'] = 1
df_avg['rolling_sum_frames_timediff_us'] = df_avg.rolling(frequency_calculation_window_size, center=True).frames_timediff_us.sum()
df_avg['rolling_sum_periody_start_mark'] = df_avg.rolling(frequency_calculation_window_size, center=True).periody_start_mark.sum()
df_avg['frequency'] = 1 / (df_avg.rolling_sum_frames_timediff_us / df_avg.rolling_sum_periody_start_mark / 10**6)

# remove NA records, bcs of rolling calculations
df_avg_filter = df_avg.dropna().copy()
df_avg_filter['frequency_rolling_mean'] = df_avg_filter.frequency.rolling(10000, center=True).quantile(0.5)
df_avg_filter['FrameTimestamp_s'] = df_avg_filter.FrameTimestamp_us / 10**6

# calculate deviation
y_0 = df_avg_filter.iloc[:1000].Edge_Avg.mean() #TODO: is it right?
print(f'Calculated zero level y_0 {y_0} for deviation calculation.')
df_avg_filter['deviation_pixel'] = y_0 - df_avg_filter.Edge_Avg
df_avg_filter['deviation_mm'] = df_avg_filter.deviation_pixel / 2 #TODO: parametrize after calibration procedure

# plot minute test summary
print('Generate output for time summary..')
t_0 = df_avg_filter.iloc[0, :].FrameTimestamp_s
df_avg_filter['elapsed_test_time_s'] = df_avg_filter.FrameTimestamp_s - t_0
df_avg_filter['elapsed_test_time_min'] = df_avg_filter.elapsed_test_time_s / 60
df_avg_filter['elapsed_test_time_min_floor'] =  np.floor(df_avg_filter.elapsed_test_time_min)

fig = px.box(df_avg_filter, x='elapsed_test_time_min_floor', y='deviation_mm', title='Deviation summary during minutes of test', labels={'elapsed_test_time_min_floor': 'Actual minute of vibration test', 'deviation_mm': 'Deviation in mm'})
fig.add_hline(y=0, line_width=1, line_dash='dash', line_color='black', opacity=0.7)
figs.append(('fig', fig))
figs.append(('table', df_avg_filter.groupby('elapsed_test_time_min_floor').deviation_mm.describe()))

# plot frequency test summary
print('Generate output for frequency summary..')
df_avg_filter['frequency_bin'] = np.nan
for f_min, f_max in [(0, 10), (10, 15), (15,20), (20,25), (25,30), (30,35), (35,40), (40,45), (45,50), (50,55), (55,65)]:
    df_avg_filter.loc[(df_avg_filter.frequency_rolling_mean > f_min) & (df_avg_filter.frequency_rolling_mean <= f_max), 'frequency_bin'] = f'({f_min}; {f_max}> Hz'
df_avg_filter.dropna(inplace=True)

fig = px.box(df_avg_filter, x='frequency_bin', y='deviation_mm', title='Deviation summary for frequencies ranges', labels={'frequency_bin': 'Frequency range during test', 'deviation_mm': 'Deviation in mm'})
fig.add_hline(y=0, line_width=1, line_dash='dash', line_color='black', opacity=0.7)
figs.append(('fig', fig))
figs.append(('table', df_avg_filter.groupby('frequency_bin').deviation_mm.describe()))

print('Creating output report..')
dashboard_html(figs, output_filename)
print(f'Output saved to file {output_filename}.')