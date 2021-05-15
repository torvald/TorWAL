import seaborn as sns
import matplotlib.pyplot as plt

import pandas as pd


class Graphs():

    def __init__(self, connetion, since, before):
        self.connetion = connetion
        self.since = since
        self.before = before

    def action(self):
        self.categories_per_day()

    def categories_per_day(self):

        sns.set_theme(style="whitegrid")
        f = plt.figure(figsize=(14, 8))
        ax = f.add_subplot(1, 1, 1)

        query = """select strftime('%Y-%m-%d',timestamp) AS 'date',
            category,
            count(*) / 6 / 60.0 as hours
            FROM x_log
            WHERE (idle < 300 or (active_win LIKE 'Meet%' and idle < 1200))
            AND 1 = 1 AND active_win not LIKE '%Race – Emilia Romagna Grand Prix%' AND active_win not LIKE '%WeeChat%'
            group by date, category
            order by date, hours
            ;"""

        df = pd.read_sql_query(query, self.connetion)

        g = sns.histplot(
            ax=ax,
            data=df,
            hue="category",
            multiple="stack",
            shrink=0.7,
            weights="hours",
            x="date",
        )

        ax.set_title("Time spent")
        ax.set_xlabel("Date")
        ax.set_ylabel("Hours")
        legend = ax.get_legend()
        legend.set_bbox_to_anchor((1, 1))
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=60)
        plt.tight_layout()
        plt.savefig("output.png")
