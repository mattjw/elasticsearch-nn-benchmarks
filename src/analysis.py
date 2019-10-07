"""Plots and other analysis."""

import os
import csv

import matplotlib.pyplot as plt
import pandas as pd

from constants import REPORTS_DIR
from experiments import REPORT_FPATH


def save_fig(name):
    plt.gcf().savefig(os.path.join(REPORTS_DIR, f"{name}.png"), bbox_inches="tight", dpi=300)
    plt.gcf().savefig(os.path.join(REPORTS_DIR, f"{name}.pdf"), bbox_inches="tight")


def normalise_method_columns(df_results, name):
    df = df_results.filter(regex=f"{name}\\.+").rename(lambda col: col.split(".")[1], axis=1)
    df.loc[:,"method"] = name
    df = pd.concat([
        df_results.filter(regex="test_case\.+").rename(lambda col: col.split(".")[1], axis=1),
        df], axis=1)
    return df


def plot_grouped(df, dependent_col):
    df = df.reset_index().loc[:, ("num_vectors", "method", dependent_col)]
    df = df.pivot(index="num_vectors", columns='method', values=dependent_col)
    df = df.rename({100: 100, 10 ** 3: "1k", 10 ** 4: "10k", 10 ** 5: "100k", 10 ** 6: "1M"}, axis=0)

    # plt.xkcd()
    df.plot.bar(rot=0, edgecolor='w', lw=0.2)
    for p in plt.gca().patches:
        if p.get_height() < 50:
            val = "{:.1f}".format(p.get_height())
        else:
            val = "{:.0f}".format(p.get_height())
        plt.gca().annotate(
            val, (p.get_x() + (p.get_width() / 2), p.get_height() + 3),
            fontsize=5,
            ha="center", va="center"
        )
    return df


def plot_query_performance(df):
    df = plot_grouped(df, "query_time_qps")
    df.to_csv(os.path.join(REPORTS_DIR, "query_performance_qps.csv"), index=True, quoting=csv.QUOTE_NONNUMERIC)

    plt.ylabel("Query rate [Queries per second]")
    plt.xlabel("Index size [Num vectors]")
    save_fig("query_performance")


def plot_insertion_performance(df):
    df = plot_grouped(df, "populate_time_ips")
    df.to_csv(os.path.join(REPORTS_DIR, "insertion_performance_ips.csv"), index=True, quoting=csv.QUOTE_NONNUMERIC)

    plt.ylabel("Insertions rate [Insertions per second]")
    plt.xlabel("Dataset size [Num vectors]")
    save_fig("insertion_performance")


def main():
    df_results = pd.read_csv(REPORT_FPATH)

    df = pd.concat(
        [normalise_method_columns(df_results, "dense"), normalise_method_columns(df_results, "fcs")],
        axis=0).set_index("fpath")

    plot_query_performance(df)
    plot_insertion_performance(df)


if __name__ == "__main__":
    main()
