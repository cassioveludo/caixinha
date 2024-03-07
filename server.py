import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import re

# Load the data from the Excel file
data = pd.read_excel('Tesouro 5_ano.xlsx')

# Calculate the total sum of Entradas + Saídas from the entire dataframe
total_sum = (data[data['movimento'] == 'entrada']['valor'].sum() +
             data[data['movimento'] == 'saída']['valor'].sum())

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    # Row 1: Title and Picture
    html.Div([
         html.Div([
             html.H1("Caixinha do 5º ano", 
                     style={'text-align': 'center', 'font-family': 'Comic Sans MS', 
                       'line-height': '80px'})],
                  style={'width': '85%'}),  
        
        html.Div([
            html.Img(src='/assets/Moara.png', 
                 style={'height': '90px', 'width': 'auto', 'align-self': 'flex-start',
                        'margin-right': '10px'})],
                 style={'width': '15%'}),
      
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),  # Adjust styles for alignment
    
    # Row 2: Inputs, Table, and Plot
    html.Div([
        # Inputs and Table
        html.Div([

            
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in data['Ano'].unique()] + 
                [{'label': 'Todos os anos', 'value': 'Todos os anos'}],
                value=datetime.now().year,
                style={'width': '125px', 'display': 'inline-block', 'margin-right': '10px'}
            ),

            
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} 
                         for month in ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro',
                                       'Dezembro']] + 
                
                [{'label': 'Todos os meses', 'value': 'Todos os meses'}],
                value=[month for month in ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio',
                                           'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro',
                                           'Novembro', 'Dezembro']]
                
                [datetime.now().month - 1],
                style={'width': '125px', 'display': 'inline-block', 'margin-right': '10px'}
            ),

            
            html.Table(
                id='sum-table',
                # style={'border': '1px solid black', 'font-size': '18px', 
                # 'display': 'inline-block', 'vertical-align': 'top', 'width': '270px', 
                # 'box-sizing': 'border-box'}
            ),

             html.Div(id='total-text', 
                      style={'font-size': '24px', 'margin-top': '50px', 'font-weight': 'bold',
                             'font-family': 'Comic Sans MS','text-align': 'center', 
                             'color': '#D98340'}),
             
             html.Div(id='last-update-text', 
                      style={'font-size': '14px', 'margin-top': '25px', 'font-weight': 'bold',
                             'font-family': 'Comic Sans MS','text-align': 'center', 
                             'color': '#333', 'font-style': 'italic'})
            
        ], style={'width': '22%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        # Plot
        html.Div([
            dcc.Graph(
                id='bar-plot',
                style={'height': '400px'}  # Adjust height as needed
            )
        ], style={'width': '78%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ]),

    # Row 3: Additional Table
    html.Div([
        html.Table(id='additional-table',
                   style={'margin-top': '20px', 'margin-left': 'auto', 'margin-right': 'auto'})
    ], style={'width': '80%', 'margin-top': '20px', 'margin-bottom': '20px', 'text-align': 'center'}),
    
])



###########################
###########################
###########################




# Define the callback function
@app.callback(
    [Output('sum-table', 'children'),
     Output('bar-plot', 'figure'),
     Output('additional-table', 'children')],
    [Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_table_and_plot(selected_year, selected_month):
    if selected_year == 'Todos os anos' and selected_month == 'Todos os meses':
        filtered_data = data
    elif selected_year == 'Todos os anos':
        filtered_data = data[data['Mês'] == selected_month]
    elif selected_month == 'Todos os meses':
        filtered_data = data[data['Ano'] == selected_year]
    else:
        filtered_data = data[(data['Ano'] == selected_year) & (data['Mês'] == selected_month)]

    # Calculate the sum for each 'movimento' type
    sum_entradas = filtered_data[filtered_data['movimento'] == 'entrada']['valor'].sum()
    sum_saidas = filtered_data[filtered_data['movimento'] == 'saída']['valor'].sum()

    # Calculate the final balance
    final_balance = sum_entradas + sum_saidas

    # Set the style for final balance
    final_balance_style = {'color': 'green' if final_balance > 0 
                           else 'black' if final_balance == 0 
                           else 'red', 'font-weight': 'bold'}

    # Create a table with the sums
    table = html.Table(
        [
            html.Tr([html.Th('Movimento'), html.Th('Valor')]),
            html.Tr([html.Td('Entradas'), html.Td(f'R$ {sum_entradas:,.2f}'.replace('.', '|').replace(',', '.').replace('|', ','), style={'color': 'green'})]),
            html.Tr([html.Td('Saídas'), html.Td(f'R$ {sum_saidas:,.2f}'.replace('.', '|').replace(',', '.').replace('|', ','), style={'color': 'darkred'})]),
            html.Tr([html.Td('Saldo'), html.Td(f'R$ {final_balance:,.2f}'.replace('.', '|').replace(',', '.').replace('|', ','), style=final_balance_style)])
        ],
        style={'border': '1px solid black', 'font-size': '18px', 'border-spacing': '10px 10px',
               'display': 'inline-block', 'vertical-align': 'top', 
               'width': '260px', 'box-sizing': 'border-box'}
          )

    # Group the data by 'movimento' and 'Descrição' and sum the 'valor'
    grouped_data_additional = filtered_data.groupby(['movimento', 'Descrição'])['valor'].sum().reset_index()

    # Create additional table
    additional_table = html.Table(
        [
            html.Tr([html.Th('Movimento'), html.Th('Descrição'), html.Th('Valor')]),
        ] +
        [
            html.Tr([
                html.Td(row['movimento']),
                html.Td(row['Descrição']),
                html.Td(f'R$ {row["valor"]:,.2f}'.replace('.', '|').replace(',', '.').replace('|', ','), 
                        style={'color': 'green' if row["valor"] >= 0 else 'darkred'})
            ]) for _, row in grouped_data_additional.iterrows()
        ],
        style={'border': '1px solid black', 'font-size': '18px', 'border-spacing': '10px 10px',
               'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center',
               'margin-top': '20px'}
    )

    # Group the data by 'Descrição' and sum the 'valor'
    grouped_data = filtered_data.groupby('Descrição')['valor'].sum().reset_index()
    
    # Filter out entries that start with 'saldo'
    grouped_data = grouped_data[~grouped_data['Descrição'].str.contains('^saldo', flags=re.IGNORECASE, regex=True)]

    # Create the bar plot
    bar_plot = px.bar(grouped_data, x='Descrição', y='valor', labels={'valor': 'Valor', 'Descrição': 'Descrição'})
    bar_plot.update_layout(
        title='<b>Detalhamento de Receitas e Despesas<b>',
        titlefont_size=20,
        xaxis_title='Receitas (azul) e Despesas (laranja)',
        yaxis_title='Reais (R$)'
    )
    
    # Make negative values in the plot bars dark red and set default bar width
    bar_plot.update_traces(marker=dict(color=['coral' if x < 0 else 'cornflowerblue' for x in grouped_data['valor']]), width=0.5)

    # Apply dynamic adjustment of plot size based on the number of bars
    if len(grouped_data) < 2:
        bar_plot.update_layout(height=400, width=500)
    elif len(grouped_data) <= 4:
        bar_plot.update_layout(height=400, width=700)
    else:
        bar_plot.update_layout(height=400, width=1000)
    
    return table, bar_plot, additional_table

# Define a callback to display the static total sum text
@app.callback(
    Output('total-text', 'children'),
    [Input('sum-table', 'children')]
)
def display_total_text(_):
    return f'Total disponível na caixinha: R$ {total_sum:,.2f}'.replace('.', '|').replace(',', '.').replace('|', ',')

# Define a callback to display the last update date
@app.callback(
    Output('last-update-text', 'children'),
    [Input('sum-table', 'children')]
)
def display_last_update(_):
    last_update_date = data['data'].max().strftime('%d/%m/%Y')
    return f'Atualizado em {last_update_date}'

# Run the app
if __name__ == '__main__':
    app.run_server(port=8053, debug = False)
