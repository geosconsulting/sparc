__author__ = 'fabio.lana'
import matplotlib.pyplot as plt
import pylab

def plot_affected(titolofinestra,nome_admin2,freq_people):

    fig = pylab.gcf()
    fig.canvas.set_window_title(titolofinestra)

    plt.grid(True)
    plt.title(nome_admin2)
    plt.xlabel("Return Periods")
    plt.ylabel("People in Flood Prone Area EM-DAT")
    plt.bar(range(len(freq_people)), freq_people.values(), align='center')
    plt.xticks(range(len(freq_people)), freq_people.keys(), rotation='vertical')
    plt.show()

def build_value_list(list_val):
    la_lista_finale = {}
    for key, val in list_val.iteritems():
        if key == 'january':
            la_lista_finale[1] = val
        elif key == 'february':
            la_lista_finale[2] = val
        elif key == 'march':
            la_lista_finale[3] = val
        elif key == 'april':
            la_lista_finale[4] = val
        elif key == 'may':
            la_lista_finale[5] = val
        elif key == 'june':
            la_lista_finale[6] = val
        elif key == 'july':
            la_lista_finale[7] = val
        elif key == 'august':
            la_lista_finale[8] = val
        elif key == 'september':
            la_lista_finale[9] = val
        elif key == 'october':
            la_lista_finale[10] = val
        elif key == 'november':
            la_lista_finale[11] = val
        elif key == 'december':
            la_lista_finale[12] = val

    for k, v in la_lista_finale.iteritems():
        if v is None:
            la_lista_finale[k] = 0

    return la_lista_finale

def plot_monthly_mean(titolofinestra,nome_admin2, list_ordered):

    fig = pylab.gcf()
    fig.canvas.set_window_title(titolofinestra)

    plt.grid(True)

    plt.plot(range(len(list_ordered)), list_ordered.values(),'b-')
    plt.xticks(range(len(list_ordered)), list_ordered.keys())
    plt.title(nome_admin2)
    plt.show()

def plot_monthly_danni(titolofinestra, labella_y, nome_admin2, list_ordered, lista_danni):

    fig = pylab.gcf()
    fig.canvas.set_window_title(titolofinestra)

    plt.grid(True)

    # Plot y1 vs x in blue on the left vertical axis.
    plt.xlabel("Months")
    plt.ylabel("Historical Incidents related with Floods EM-DAT", color="b")
    plt.tick_params(axis="y", labelcolor="b")
    plt.bar(range(len(lista_danni)), lista_danni.values(), align='center', color='g',label='Incidents')

    plt.twinx()
    plt.ylabel(labella_y, color="r")
    plt.tick_params(axis="y", labelcolor="r")
    plt.plot(range(len(list_ordered)), list_ordered.values(), 'r--')
    plt.xticks(range(len(list_ordered)), list_ordered.keys())

    plt.title(nome_admin2)
    plt.legend()
    plt.show()

def plot_monthly_mean_wb(nome_paese, lista_valori):

    fig = pylab.gcf()
    fig.canvas.set_window_title(nome_paese)

    plt.grid(True)
    plt.title("World Bank Historical Data on Precipitation")
    # Plot y1 vs x in blue on the left vertical axis.
    plt.xlabel("Months")
    plt.ylabel("Precipitation", color="r")

    finale = {}
    mese = 1
    for valore in lista_valori:
        finale[mese] = valore
        mese += 1

    # plt.plot(range(len(finale)), finale.values(), 'r-')
    # plt.fill_between(range(len(finale)), finale.values(), facecolor='blue', alpha=0.5)
    # plt.show()

    return finale

def plot_monthly_persone_danneggiate_finale(titolofinestra, labella_y, nome_admin2, lista_tutti_rp):

    fig = pylab.gcf()
    fig.canvas.set_window_title(titolofinestra)
    plt.grid(True)

    mesi = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    plt.xlabel("Months",color="r")
    plt.ylabel("People possibly affected", color="r")
    plt.tick_params(axis="x", labelcolor="r")
    plt.tick_params(axis="y", labelcolor="r")

    plt.plot(range(len(lista_tutti_rp['25'])), lista_tutti_rp['25'].values(),'bo-', markersize=8, label="25 Years")
    plt.plot(range(len(lista_tutti_rp['50'])), lista_tutti_rp['50'].values(), 'ro-', markersize=8, label="50 Years")
    plt.plot(range(len(lista_tutti_rp['100'])), lista_tutti_rp['100'].values(), 'go-', markersize=8, label="100 Years")
    plt.plot(range(len(lista_tutti_rp['200'])), lista_tutti_rp['200'].values(), 'yo-', markersize=8, label="200 Years")
    #plt.plot(range(len(lista_tutti_rp['500'])), lista_tutti_rp['500'].values(), 'ko--', marker = 'o',markersize = 4,label = "500 Years")
    #plt.plot(range(len(lista_tutti_rp['1000'])), lista_tutti_rp['1000'].values(), 'mo--', marker = 'o', markersize = 4, label = "1000 Years")

    plt.xticks(range(len(mesi)), mesi)
    plt.title(nome_admin2)
    plt.legend()
    plt.show()

def plottalo_bello(data, nome_admin2):

    import numpy as np
    import math

    columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    rows = ['%d RP' % x for x in (1000, 500, 200, 100, 50, 25)]

    matrice = np.asarray(data)
    maximo_y = math.ceil(max(matrice.sum(0))/500)*500

    values = np.arange(0, maximo_y, 100000)
    #values = np.arange(0, 600, 100)
    value_increment = 1

    # Get some pastel shades for the colors
    colors = plt.cm.OrRd(np.linspace(0, 0.5, len(rows)))
    n_rows = len(data)

    #index = np.arange(len(columns)) + 0.3
    index = np.arange(len(columns))
    bar_width = 1

    # Initialize the vertical-offset for the stacked bar chart.
    y_offset = np.array([0.0] * len(columns))

    # Plot bars and create text labels for the table
    cell_text = []
    for row in range(n_rows):
        plt.bar(index, data[row], bar_width, bottom=y_offset, color=colors[row])
        y_offset = y_offset + data[row]
        cell_text.append(['%d' % (x) for x in y_offset])
    # Reverse colors and text labels to display the last value at the top.
    colors = colors[::-1]
    cell_text.reverse()

    # Add a table at the bottom of the axes
    the_table = plt.table(cellText=cell_text,
                          rowLabels=rows,
                          rowColours=colors,
                          colLabels=columns,
                          loc ='bottom')

    # Adjust layout to make room for the table:
    plt.subplots_adjust(left=0.2, bottom=0.2)

    plt.ylabel("People at risk per Return Period")
    plt.yticks(values * value_increment), ['%d' % val for val in values]
    plt.xticks([])
    plt.title('People at risk by Return Period in ' + nome_admin2)
    plt.show()
