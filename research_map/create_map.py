"""Career-path map of Europe for an introduction slide.

Numbered, colour-blind-safe markers (Okabe-Ito colours + different marker
shapes), each with a callout box, joined by arrows along the ROUTE.

Outputs career_map.png (300 dpi) and career_map.svg (text stays editable).
Edit the STOPS and ROUTE lists below; tweak `box_xy` (axes fraction) to move a
callout.
Cartopy downloads Natural Earth data on first use (needs internet once).
"""
from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, TextArea, VPacker
from matplotlib.patches import FancyArrowPatch

# Keep text as real text in the SVG so it can be edited in Inkscape / PowerPoint.
plt.rcParams["svg.fonttype"] = "none"

OCEAN = "#E3EAF0"
LAND = "#F4F2EE"
EDGE = "#B9B9B9"
INK = "#222222"

# Sizes in points on the 16:9 figure. If you rescale the text, move the
# callouts (`box_xy`) to match: the boxes grow with the text.
TITLE_SIZE = 34
SUBTITLE_SIZE = 24  # set on the same line, right of the title
HEADING_SIZE = 25  # callout heading, e.g. "1  Vienna"
BODY_SIZE = 19  # years, role and summary in a callout
NUMBER_SIZE = 18  # number inside a marker
CREDIT_SIZE = 11
MARKER_SIZE = 36
WRAP_WIDTH = 34  # characters per callout line


@dataclass(frozen=True)
class Stop:
    """One research station on the map, drawn as a numbered marker with a callout.

    Attributes:
        name: Place name shown as the callout heading.
        lat: Latitude of the marker (deg).
        lon: Longitude of the marker (deg).
        years: Time span shown in front of the role, e.g. "2019 - 2025".
        role: Position and institution.
        summary: Short description of the research done there.
        color: Marker and callout-frame colour (Okabe-Ito hex code).
        marker: Matplotlib marker shape, distinct for every stop.
        num_color: Colour of the number inside the marker, chosen for contrast.
        box_xy: Top-left corner of the callout box, in axes fraction.
    """

    name: str
    lat: float
    lon: float
    years: str
    role: str
    summary: str
    color: str  # Okabe-Ito
    marker: str  # distinct shape per stop
    num_color: str  # number colour inside the marker (contrast)
    box_xy: tuple[float, float]  # callout top-left, axes fraction


# One entry per place, in order of first visit (the marker numbers follow this list).
STOPS: list[Stop] = [
    Stop(
        name="Vienna",
        lat=48.2082,
        lon=16.3738,
        years="2019 - 2025",
        role="Bachelor's & Master's, University of Vienna",
        summary="Evolution of protoplanetary discs",
        color="#0072B2",
        marker="o",
        num_color="white",
        box_xy=(0.61, 0.82),
    ),
    Stop(
        name="Garching (Munich)",
        lat=48.2587,
        lon=11.6711,
        years="2025",
        role="Research internship, ESO",
        summary="Automatic classification in time-series observations",
        color="#E69F00",
        marker="s",
        num_color="black",
        box_xy=(0.10, 0.40),
    ),
    Stop(
        name="Aachen",
        lat=50.7753,
        lon=6.0839,
        years="2025 - today",
        role="PhD, RWTH Aachen",
        summary="3D Bayesian inference of Milky Way gas and dust",
        color="#D55E00",
        marker="D",
        num_color="white",
        box_xy=(0.01, 0.82),
    ),
]

# Chronological path through the STOPS, by name; a place may appear more than once.
# The internship at ESO was during the Master's, which was finished in Vienna.
ROUTE: list[str] = ["Vienna", "Garching (Munich)", "Vienna", "Aachen"]


def build(out_dir: Path, stem: str, title: str, subtitle: str) -> None:
    """Draw the map of all STOPS and save it as PNG (300 dpi) and SVG.

    Args:
        out_dir: Directory to write the images to; created if it does not exist.
        stem: File name without extension, shared by both outputs.
        title: Bold heading printed in the top-left corner of the figure.
        subtitle: Smaller grey text on the same line, right of the title.
    """
    pc = ccrs.PlateCarree()
    proj = ccrs.LambertConformal(
        central_longitude=11.0, central_latitude=50.0, standard_parallels=(45, 55)
    )

    fig = plt.figure(figsize=(13.333, 7.5))  # 16:9 slide
    fig.patch.set_facecolor(OCEAN)
    ax = fig.add_axes([0, 0, 1, 1], projection=proj)
    ax.set_extent([-3.0, 23.0, 44.0, 55.5], crs=pc)
    ax.set_facecolor(OCEAN)
    ax.spines["geo"].set_visible(False)

    # Muted basemap so markers and callouts carry the slide.
    ax.add_feature(
        cfeature.NaturalEarthFeature(
            "physical", "land", "50m", facecolor=LAND, edgecolor=EDGE, linewidth=0.6
        ),
        zorder=1,
    )
    ax.add_feature(
        cfeature.NaturalEarthFeature(
            "cultural",
            "admin_0_boundary_lines_land",
            "50m",
            facecolor="none",
            edgecolor=EDGE,
            linewidth=0.6,
        ),
        zorder=2,
    )

    xy = [proj.transform_point(s.lon, s.lat, pc) for s in STOPS]
    xy_by_name = {s.name: p for s, p in zip(STOPS, xy, strict=True)}

    # Chronological arrows along the route. The curvature bends each arrow to
    # the same side of its direction of travel, so an out-and-back pair (Vienna
    # -> Garching -> Vienna) splits into two separate arcs instead of overlapping.
    for start, end in zip(ROUTE[:-1], ROUTE[1:], strict=True):
        ax.add_patch(
            FancyArrowPatch(
                xy_by_name[start],
                xy_by_name[end],
                arrowstyle="-|>",
                mutation_scale=20,
                lw=2.4,
                color=INK,
                shrinkA=MARKER_SIZE * 2 / 3,  # stop just outside the markers
                shrinkB=MARKER_SIZE * 2 / 3,
                connectionstyle="arc3,rad=0.2",
                zorder=4,
            )
        )

    for i, (s, (x, y)) in enumerate(zip(STOPS, xy, strict=True), start=1):
        ax.plot(
            x,
            y,
            marker=s.marker,
            ms=MARKER_SIZE,
            mfc=s.color,
            mec="white",
            mew=2.2,
            zorder=5,
        )
        ax.text(
            x,
            y,
            str(i),
            ha="center",
            va="center",
            color=s.num_color,
            fontsize=NUMBER_SIZE,
            fontweight="bold",
            zorder=6,
        )

        box = VPacker(
            children=[
                TextArea(
                    f"{i}  {s.name}",
                    textprops=dict(fontsize=HEADING_SIZE, fontweight="bold", color=INK),
                ),
                TextArea(
                    textwrap.fill(
                        s.role,
                        WRAP_WIDTH,
                        initial_indent=f"{s.years}  ·  ",
                        break_on_hyphens=False,
                    ),
                    textprops=dict(fontsize=BODY_SIZE, color="#444444"),
                ),
                TextArea(
                    textwrap.fill(s.summary, WRAP_WIDTH, break_on_hyphens=False),
                    textprops=dict(fontsize=BODY_SIZE, color=INK),
                ),
            ],
            align="left",
            pad=0,
            sep=7,
        )
        ax.add_artist(
            AnnotationBbox(
                box,
                xy=(x, y),
                xycoords="data",
                xybox=s.box_xy,
                boxcoords="axes fraction",
                box_alignment=(0, 1),
                frameon=True,
                pad=0.6,
                bboxprops=dict(
                    boxstyle="round,pad=0.8", fc="white", ec=s.color, lw=2.6
                ),
                arrowprops=dict(
                    arrowstyle="-",
                    color=s.color,
                    lw=1.8,
                    shrinkA=0,
                    shrinkB=MARKER_SIZE / 2 + 2,
                ),
                zorder=7,
            )
        )

    title_text = fig.text(
        0.03, 0.95, title, fontsize=TITLE_SIZE, fontweight="bold", color=INK, va="top"
    )
    # Anchored to the bottom-right corner of the title, so it follows the title's
    # length and size. Bottoms line up, which matches the baselines as long as
    # both texts have descenders (as "y" in both of them does).
    ax.annotate(
        subtitle,
        xy=(1, 0),
        xycoords=title_text,
        xytext=(SUBTITLE_SIZE * 0.75, 0),
        textcoords="offset points",
        va="bottom",
        fontsize=SUBTITLE_SIZE,
        color="#444444",
        annotation_clip=False,
    )
    fig.text(
        0.99,
        0.012,
        "Map data: Natural Earth",
        fontsize=CREDIT_SIZE,
        color="#666666",
        ha="right",
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    for ext, kw in (("png", {"dpi": 300}), ("svg", {})):
        path = out_dir / f"{stem}.{ext}"
        fig.savefig(path, facecolor=fig.get_facecolor(), **kw)
        print(f"wrote {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out-dir", type=Path, default=Path("."))
    p.add_argument("--stem", default="career_map")
    p.add_argument("--title", default="Fabian Polnitzky")
    p.add_argument("--subtitle", default="Where my research happens")
    args = p.parse_args()
    build(args.out_dir, args.stem, args.title, args.subtitle)
