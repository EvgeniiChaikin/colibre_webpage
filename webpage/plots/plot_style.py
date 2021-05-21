import matplotlib.pylab as plt
from matplotlib.ticker import AutoMinorLocator


def import_style(style: str):
    """
    Load matplotlib style
    """
    plt.style.use(style)
    return


def create_plot_with_style(x_size, y_size):

    plt.rcParams["figure.figsize"] = x_size, y_size
    fig, ax = plt.subplots()

    x_minor_locator = AutoMinorLocator(5)
    y_minor_locator = AutoMinorLocator(5)
    ax.xaxis.set_minor_locator(x_minor_locator)
    ax.yaxis.set_minor_locator(y_minor_locator)

    plt.tick_params(which="both", width=1.7)
    plt.tick_params(which="major", length=9)
    plt.tick_params(which="minor", length=5)

    ax.tick_params(
        axis="both", which="both", pad=8, left=True, right=True, top=True, bottom=True
    )

    fig.set_tight_layout(False)

    return fig, ax