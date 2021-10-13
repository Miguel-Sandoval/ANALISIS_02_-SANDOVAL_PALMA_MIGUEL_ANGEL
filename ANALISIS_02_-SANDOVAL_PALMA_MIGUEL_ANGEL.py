import pandas as pd
import operations as op
import sys
import pandas as pd


def get_routes(dataframe):
    """
    Function that calculate the total value and total sales per route

    :param dataframe: a dataframe that has the original information
    :return: the modified dataframe
    """
    # Get the yearly sum of the sales per route
    dataframe = dataframe.drop(columns='direction')
    dataframe = dataframe.groupby(['origin', 'destination', 'year'], sort=False).agg(
        total_value=pd.NamedAgg(column='total_value', aggfunc='sum'),
        total_sales=pd.NamedAgg(column='total_value', aggfunc='count'))

    # Get the mean total_value per route
    dataframe = dataframe.reset_index().drop(columns='year')
    dataframe = dataframe.groupby(['origin', 'destination'], sort=False).agg(
        avg_total_value=pd.NamedAgg(column='total_value', aggfunc='mean'),
        total_sales=pd.NamedAgg(column='total_sales', aggfunc='sum'))
    dataframe = dataframe.reset_index()

    return dataframe


def sort_routes_by_index(dataframe):
    """
    Function that create a column that holds the value of an index
    which helps to sort the routes based on it.

    :param dataframe: a dataframe that has the routes
    :return: the dataframe with the data sorted by the index

    """
    # We need to normalize using feature scaling the avg_total_value and total_sales,
    # add them together by using a weighted average and sort them in descending order

    # Get the min and max values of each column
    max_avg_total_value = dataframe['avg_total_value'].max()
    max_total_sales = dataframe['total_sales'].max()
    min_avg_total_value = dataframe['avg_total_value'].min()
    min_total_sales = dataframe['total_sales'].min()

    # Use this statistics to normalize and create an index to sort the routes
    scaled_avg_total_value = (dataframe['avg_total_value'] - min_avg_total_value) / \
                             (max_avg_total_value - min_avg_total_value)
    scaled_total_sales = (dataframe['total_sales'] - min_total_sales) / (max_total_sales - min_total_sales)

    # We perform an arithmetic mean to get the index
    dataframe['index'] = (scaled_avg_total_value + scaled_total_sales) / 2

    dataframe = dataframe.sort_values(by='index', ascending=False)

    return dataframe



synergy_logistics_info_df = pd.read_csv('synergy_logistics_database.csv', usecols=lambda x: x != 'register_id')


def option_1():
    """Rutas de importación y exportación. Synergy logistics está
considerando la posibilidad de enfocar sus esfuerzos en las 10 rutas más
demandadas. Acorde a los flujos de importación y exportación, ¿cuáles son esas
10 rutas? ¿le conviene implementar esa estrategia? ¿porqué? 
    """
    # copy the dataframe to avoid modifying it
    option_1_df = synergy_logistics_info_df.copy()
    option_1_df.drop(columns=['product', 'transport_mode', 'date', 'company_name'], inplace=True)

    # divide in two df, one for imports and the other for exports
    option_1_df_exports = option_1_df[option_1_df['direction'] == 'Exports']
    option_1_df_imports = option_1_df[option_1_df['direction'] == 'Imports']

    option_1_df_exports = get_routes(option_1_df_exports)
    option_1_df_imports = get_routes(option_1_df_imports)

    option_1_df_exports = sort_routes_by_index(option_1_df_exports).reset_index(drop=True)
    option_1_df_imports = sort_routes_by_index(option_1_df_imports).reset_index(drop=True)

    option_1_df_exports.index = option_1_df_exports.index + 1
    option_1_df_imports.index = option_1_df_imports.index + 1
    print('Top 10 rutas exportacion:')
    print(option_1_df_exports[:10])
    print('\n')
    print('Top 10 rutas importacion:')
    print(option_1_df_imports[:10])


def option_2():
   #Función que ordena los datos por medio de transporte y su valor total asociado y lo muestra en pantalla
    option_2_df = synergy_logistics_info_df.copy()
    option_2_df = option_2_df.drop(columns=['origin', 'destination', 'year', 'date', 'product', 'company_name'])
    print(option_2_df.groupby(['transport_mode', 'direction']).sum().sort_values(by='total_value', ascending=False))
    print("\n")
    print(option_2_df.groupby(['transport_mode']).sum().sort_values(by='total_value', ascending=False))


def option_3():
    #Función que calcula que calcula el porcentaje acumulado del valor total para cada país y lo muestra en pantalla
    option_3_df = synergy_logistics_info_df.copy()
    option_3_df['country'] = option_3_df.apply(
        lambda row: row['origin'] if row['direction'] == 'Exports' else row['destination'], axis=1)
    option_3_df = option_3_df[['country', 'total_value']]
    option_3_df = option_3_df.groupby('country').sum()
    option_3_df = option_3_df.sort_values(by='total_value', ascending=False)
    option_3_df['cumulative_percentage'] = 100 * option_3_df['total_value'].cumsum() / option_3_df['total_value'].sum()
    print(option_3_df)



def el_menu(option):
    #Funcion menu para acceder a las funciones diseñadas
    switcher = {
        1: option_1,
        2: option_2,
        3: option_3
    }
    func = switcher.get(option, "Opcion no valida, ERROR 404 NOT FOUND")
    return func()


finish = 'n'

while finish != ('y' or 'Y'):
    print('''
    Opciones disponibles:
        1. Analiza las rutas de exportación e importación y da un top 10 para cada una de ellas.
        2. Ordenar los medios de transporte según los ingresos. 
        3. Ingresos totales por importación y exportación y los países que generan 80% de ingresos para la empresa.
    ''')

    el_menu(int(input('Digita la opcion deseada: ')))
    finish = input('Quieres salir ? (y/n): ')
