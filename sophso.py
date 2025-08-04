from plotnine.geoms import geom_point
from plotnine.doctools import document
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image
import urllib

import numpy as np

from itscalledsoccer.client import AmericanSoccerAnalysis


asa_client = AmericanSoccerAnalysis()


@document
class geom_image(geom_point):
    """
    Plot Images with plotnine
    Based on geom_point
    Instead of points, plots images at those points

    Args:
        geom : ggplot geom
    """

    DEFAULT_AES = {"size": 0.1, "alpha": 1}  # , "color": None, "fill": "#333333",
    # "linetype": "solid", "size": 0.5 }
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }  # no idea if I need this
    REQUIRED_AES = {"x", "y", "image"}  # just need an image column

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        assume only one image per panel,
        """
        data = coord.transform(data, panel_params)
        self.draw_unit(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params)
        units = "shape"
        for _, udata in data.groupby(units, dropna=False):
            udata.reset_index(inplace=True, drop=True)
            geom_image.draw_unit(udata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_unit(data, panel_params, coord, ax, **params):
        for i in range(len(data)):
            img = data["image"].iloc[i]
            zoom = data["size"].iloc[i]
            ab = AnnotationBbox(
                OffsetImage(
                    np.array(Image.open(urllib.request.urlopen(img))),
                    zoom=zoom,
                    alpha=data["alpha"].iloc[i],
                ),
                (data["x"].iloc[i], data["y"].iloc[i]),
                frameon=False,
                box_alignment=(0.5, 0),
            )
            ax.add_artist(ab)


def decorate_team_ids(df):
    team_ids = set()

    for c in df.columns:
        if "team_id" in c:
            team_ids |= set(df[c].unique())

    teams_df = asa_client.get_teams(ids=list(team_ids))
    team_map = dict(zip(teams_df.team_id, teams_df.team_abbreviation))

    for c in df.columns:
        if "team_id" in c:
            df[c.replace("team_id", "team")] = df[c].map(team_map)
            df[c.replace("team_id", "team_logo")] = (
                "https://american-soccer-analysis-headshots.s3.amazonaws.com/club_logos/"
                + df[c]
                + ".png"
            )

    return df


def decorate_player_ids(df):
    player_ids = set()

    for c in df.columns:
        if "player_id" in c:
            player_ids |= set(df[c].unique())

    players_df = asa_client.get_players(ids=list(player_ids))
    player_map = dict(zip(players_df.player_id, players_df.player_name))

    for c in df.columns:
        if "player_id" in c:
            df[c.replace("player_id", "player")] = df[c].map(player_map)
            df[c.replace("player_id", "player_headshot")] = (
                "https://american-soccer-analysis-headshots.s3.amazonaws.com/player_headshots/"
                + df[c]
                + ".png"
            )

    return df


nwsl_primary_colors = {
    "HOU": "#ff6800",  # Houston Dash - Electric Orange
    "KC": "#CB333B",  # Kansas City Current - Red
    "SD": "#fc1896",  # San Diego Wave FC - Pink
    "SEA": "#003087",  # Seattle Reign FC - Blue
    "WAS": "#051C2C",  # Washington Spirit - Dark Blue
    "POR": "#971e1f",  # Portland Thorns FC - Red
    "CHI": "#d71d28",  # Chicago Red Stars - Red
    "LOU": "#C5B4E3",  # Racing Louisville FC - Lavender
    # 'LOU': '#1E1A34',  # Racing Louisville FC - Lavender
    "LA": "#f1b1a5",  # Angel City FC - Sol Rosa
    # 'LA': '#F2D4D7',   # Angel City FC - Sol Rosa
    # "NJY": "#9ADBE8",  # NJ/NY Gotham FC - Sky Blue
    "NJY": "#010101",  # Gotham Black
    "NC": "#01426A",  # North Carolina Courage - Atlantic Blue
    "ORL": "#633294",  # Orlando Pride - Purple
    "UTA": "#feb71b",  # Utah Royals FC - Cobalt Blue
    "BAY": "#051C2C",  # Bay FC - Bay
}
