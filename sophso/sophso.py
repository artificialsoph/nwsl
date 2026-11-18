from plotnine.geoms import geom_point
from plotnine.doctools import document
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image
import urllib

import numpy as np
import pandas as pd

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


def decorate_game_ids(df):
    game_ids = set(df.game_id.to_list())

    games_df = decorate_team_ids(asa_client.get_games(game_ids=list(game_ids)))
    games_df["game_desc"] = (
        games_df.home_team
        + " vs "
        + games_df.away_team
        + ": "
        + pd.to_datetime(games_df.date_time_utc).dt.strftime("%Y-%m-%d")
    )

    games_df["score_desc"] = (
        games_df.home_score.astype("str") + " - " + games_df.away_score.astype("str")
    )

    desc_map = dict(zip(games_df.game_id, games_df.game_desc))
    date_map = dict(zip(games_df.game_id, games_df.date_time_utc))
    score_map = dict(zip(games_df.game_id, games_df.score_desc))

    df["game_desc"] = df["game_id"].map(desc_map)
    df["date_time_utc"] = pd.to_datetime(df["game_id"].map(date_map))
    df["score_desc"] = df["game_id"].map(score_map)

    return df


nwsl_primary_colors = {
    "HOU": "#ff6800",  # Houston Dash - Electric Orange
    "KC": "#62ccca",  # Kansas City Current - Teal
    "SD": "#fc1896",  # San Diego Wave FC - Pink
    "SEA": "#d0a66b",  # Seattle Reign FC - Gold
    "WAS": "#051C2C",  # Washington Spirit - Dark Blue
    "POR": "#971e1f",  # Portland Thorns FC - Red
    "CHI": "#37b5e9",  # Chicago Red Stars - Red
    "LOU": "#C5B4E3",  # Racing Louisville FC - Lavender
    "LA": "#f1b1a5",  # Angel City FC - Sol Rosa
    "NJY": "#a8f0f6",  # Gotham
    "NC": "#03406a",  # North Carolina Courage - Atlantic Blue
    "ORL": "#633294",  # Orlando Pride - Purple
    "UTA": "#fcb913",  # Utah Royals FC - Gold
    "BAY": "#031b2e",  # Bay FC - Bay
    "BOS": "#32e983",  # Boston legacy
    "DEN": "#195f4c",  # Denver Summit
}

nwsl_secondary_colors = {
    "HOU": "#8eb8e2",  # Houston Dash - Space City Navy
    "KC": "#EF3E42",  # Kansas City Current - Roster Red
    "SD": "#012a62",  # San Diego Wave FC - Pacific Navy
    "SEA": "#0B1F3A",  # Seattle Reign FC - Reign Navy
    "WAS": "#f3fb62",  # Washington Spirit - Highlighter Yellow
    "POR": "#000000",  # Portland Thorns FC - Black
    "CHI": "#E81F36",  # Chicago Stars - Stars Red
    "LOU": "#c4f1d4",  # Racing Louisville FC - Mint
    "LA": "#000000",  # Angel City FC - Armour Black
    "NJY": "#000000",  # Gotham FC - Black
    "NC": "#C8102E",  # North Carolina Courage - Carolina Red
    "ORL": "#01a8e2",  # Orlando Pride - Teal
    "UTA": "#215ca5",  # Utah Royals FC - Cobalt Blue
    "BAY": "#f9423a",  # Bay FC - Poppy Red
    "BOS": "#000000",  # Boston Legacy - White
    "DEN": "#c14b34",  # Denver Summit - Sunset Red/Orange
}
