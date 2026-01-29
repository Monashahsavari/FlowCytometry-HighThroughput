import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import LogLocator
import warnings


def sci_format(x):
    if x == 0:
        return 0
    pattern = r"{0:.0f}$\times$$10^{1:.0f}$".format(
        np.sign(x) * 10 ** (-np.floor(np.log10(abs(x))) + np.log10(abs(x))),
        np.floor(np.log10(abs(x))))

    return pattern

major_formatter = FuncFormatter(sci_format)


def format_axis(
    fig,
    axs,
    xlabel,
    ylabel,
    xlim_left,
    xlim_right,
    ylim_bottom,
    ylim_top,
    nx_ticks,
    ny_ticks,
    ylabel_padding=20,
    scientific_x=False,
    scientific_y=False,
    fontsize=36,
    log_y=False,
):
    """
    Function to add styling to Axes.

    Example:

    fig, axs = plt.subplots(1, 1, figsize=(10, 10))
    axs.plot(np.arange(0, 100), np.arange(0, 100))
    format_axis(fig, axs, 'LALS (a.u.)', 'Counts', 0, 300, 1, 4000, 6, 6, log_y=True, fontsize=40, scientific_y=True)
    plt.show()

    :param axs: Matplotlib Axes to style
    :param xlabel: x label
    :param ylabel: y label
    :param xlim_left: lower limit of the x-axis
    :param xlim_right: upper limit of the x-axis
    :param ylim_bottom: lower limit of the y-axis
    :param ylim_top: upper limit of the y-axis
    :param nx_ticks: number of major x ticks
    :param ny_ticks: number of major y ticks
    :param ylabel_padding: extra padding between y-axis label and y tick labels
    :param scientific_x: scientific notation x-axis
    :param scientific_y: scientific notation y-axis
    :param fontsize:
    :param log_y: log scale for y-axis
    :return:
    """

    if nx_ticks > 6 or ny_ticks > 6:
        warnings.warn("Consider using no more than 6 tick marks per axis")

    if scientific_x:
        axs.xaxis.set_major_formatter(major_formatter)
    if scientific_y:
        axs.yaxis.set_major_formatter(major_formatter)
    plt.rcdefaults()
    plt.rcParams.update({'font.size': 36, 'font.family': 'Calibri', 'font.style': 'normal'})

    plt.setp(axs.spines.values(), linewidth=3)
    plt.yticks(fontsize=fontsize, rotation=0)
    plt.xticks(fontsize=fontsize, rotation=0)

    axs.set_ylim(bottom=ylim_bottom)
    axs.set_ylim(top=ylim_top)

    axs.set_xlim(left=xlim_left)
    axs.set_xlim(right=xlim_right)

    # twin_ay = fig.add_axes(axs.get_position())
    # twin_ay.set_facecolor("None")
    # twin_ay.set_aspect('equal')
    # twin_ay.tick_params(bottom=0, top=1, left=0, right=1,
    #                 labelbottom=0, labeltop=1, labelleft=0, labelright=1)

    # Add twin axis
    twin_ay = axs.twinx()
    twin_ax = axs.twiny()

    axs.tick_params(
        axis="y",
        direction="out",
        which="major",
        length=10,
        width=4,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    axs.tick_params(
        axis="y",
        which="minor",
        direction="out",
        length=7,
        width=2,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    twin_ay.tick_params(
        axis="y",
        which="major",
        direction="in",
        length=10,
        width=4,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    twin_ay.tick_params(
        axis="y",
        which="minor",
        direction="in",
        length=7,
        width=2,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    axs.tick_params(
        axis="x",
        which="major",
        direction="out",
        length=10,
        width=4,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    axs.tick_params(
        axis="x",
        which="minor",
        direction="out",
        length=7,
        width=2,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    twin_ax.tick_params(
        axis="x",
        which="minor",
        direction="in",
        length=7,
        width=2,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )
    twin_ax.tick_params(
        axis="x",
        which="major",
        direction="in",
        length=10,
        width=4,
        colors="k",
        grid_color="k",
        grid_alpha=0.5,
        pad=25,
    )



    twin_ax.set_xlim(axs.get_xlim())
    twin_ay.set_ylim(axs.get_ylim())
    twin_ay.yaxis.set_ticklabels([])
    twin_ax.xaxis.set_ticklabels([])
    axs.set_ylabel(ylabel, fontname="Calibri", fontsize=fontsize, labelpad=ylabel_padding)
    axs.set_xlabel(xlabel, fontname="Calibri", fontsize=fontsize, labelpad=20)

    axs.xaxis.set_major_locator(plt.LinearLocator(nx_ticks))
    axs.xaxis.set_minor_locator(plt.LinearLocator((nx_ticks * 2) - 1))
    twin_ax.xaxis.set_major_locator(plt.LinearLocator(nx_ticks))
    twin_ax.xaxis.set_minor_locator(plt.LinearLocator((nx_ticks * 2) - 1))

    if log_y:
        axs.set_yscale("log")
        twin_ay.set_yscale("log")

        axs.yaxis.set_major_locator(LogLocator(base=10))
        twin_ay.yaxis.set_major_locator(LogLocator(base=10))
        twin_ay.yaxis.set_ticklabels([])
        twin_ax.xaxis.set_ticklabels([])

    else:
        axs.yaxis.set_major_locator(plt.LinearLocator(ny_ticks))
        axs.yaxis.set_minor_locator(plt.LinearLocator((ny_ticks * 2) - 1))

        twin_ay.yaxis.set_major_locator(plt.LinearLocator(ny_ticks))
        twin_ay.yaxis.set_minor_locator(plt.LinearLocator((ny_ticks * 2) - 1))

    # Remain aspect ratio of 1 to keep fig square
    axs.set_box_aspect(1)

    # Make sure the large axis labels and tick marks dont fall of when showing the figure
    fig.set_tight_layout(True)

    return axs


