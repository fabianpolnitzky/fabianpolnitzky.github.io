"""Career-path map of Europe for an introduction slide.

Numbered, colour-blind-safe markers (Okabe-Ito colours + different marker
shapes), each with a callout box, joined by arrows along the ROUTE.

Outputs career_map.png (300 dpi) and career_map.svg (text stays editable).
Edit the STOPS and ROUTE lists below. Callouts are placed automatically where
they cover nothing else; set `box_xy` (axes fraction) on a stop to pin its
callout by hand.
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
import numpy as np

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

# Sizes in points on the 16:9 figure. The callouts grow with the text and are
# re-placed automatically, except for those pinned with `box_xy`.
TITLE_SIZE = 34
SUBTITLE_SIZE = 24  # set on the same line, right of the title
HEADING_SIZE = 25  # callout heading, e.g. "1  Vienna"
BODY_SIZE = 19  # years, role and summary in a callout
NUMBER_SIZE = 18  # number inside a marker
CREDIT_SIZE = 11
MARKER_SIZE = 36
WRAP_WIDTH = 34  # characters per callout line
CLEARANCE = 8  # free space kept around automatically placed callouts


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
        supervisors: Names, appended to the role as "Supervised by ..."; leave
            empty to omit.
        box_xy: Top-left corner of the callout box, in axes fraction, to pin it
            by hand; None places it automatically (see `place_callouts`).
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
    supervisors: str = ""
    box_xy: tuple[float, float] | None = None


# One entry per place, in order of first visit (the marker numbers follow this list).
STOPS: list[Stop] = [
    Stop(
        name="Vienna",
        lat=48.2082,
        lon=16.3738,
        years="2019 - 2025",
        role="Bachelor's & Master's, University of Vienna",
        supervisors="João Alves",
        summary="Evolution of protoplanetary discs",
        color="#0072B2",
        marker="o",
        num_color="white",
    ),
    Stop(
        name="Garching (Munich)",
        lat=48.2587,
        lon=11.6711,
        years="2025",
        role="Research internship, ESO",
        supervisors="Amelia Bayo & Paula Sánchez Sáez",
        summary="Automatic classification in time-series observations",
        color="#E69F00",
        marker="s",
        num_color="black",
    ),
    Stop(
        name="Aachen",
        lat=50.7753,
        lon=6.0839,
        years="2025 - today",
        role="PhD, RWTH Aachen",
        supervisors="Philipp Mertsch",
        summary="3D Bayesian inference of Milky Way gas and dust",
        color="#D55E00",
        marker="D",
        num_color="white",
    ),
]

# Chronological path through the STOPS, by name; a place may appear more than once.
# The internship at ESO was during the Master's, which was finished in Vienna.
ROUTE: list[str] = ["Vienna", "Garching (Munich)", "Vienna", "Aachen"]


def _sample_polyline(vertices: np.ndarray, step: float) -> np.ndarray:
    """Points along a polyline, at most `step` apart (same units as `vertices`)."""
    points = [vertices[:1]]
    for a, b in zip(vertices[:-1], vertices[1:], strict=True):
        n = max(int(np.hypot(*(b - a)) // step), 1)
        points.append(a + (b - a) * np.linspace(0, 1, n + 1)[1:, None])
    return np.vstack(points)


def place_callouts(
    fig: plt.Figure,
    ax: plt.Axes,
    callouts: list[tuple[Stop, AnnotationBbox, tuple[float, float]]],
    arrows: list[FancyArrowPatch],
    texts: list[plt.Artist],
) -> None:
    """Move every callout without a manual `box_xy` to a free spot near its marker.

    Pinned callouts stay put and count as obstacles. The others are placed one by
    one, in STOPS order, by trying every position inside the map on a fine grid
    and keeping the cheapest one. The cost is dominated by overlap with what is
    already there (markers, arrows, the given texts, callouts placed so far,
    each with CLEARANCE around it); among free positions, it prefers a short but
    visible connecting line to the marker.

    Args:
        fig: Figure with everything drawn except the final callout positions.
        ax: Map axes; callouts are kept inside it.
        callouts: (stop, callout, marker position in data coordinates) per stop.
        arrows: Route arrows, which the callouts must not cover.
        texts: Further artists the callouts must not cover, such as the title.

    Raises:
        ValueError: If a callout is too large to fit inside the map at all.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    pt = fig.dpi / 72  # display pixels per point
    clear = CLEARANCE * pt
    step = 3 * pt  # grid spacing of candidate positions
    leader = 1.5 * MARKER_SIZE * pt  # preferred marker-to-box distance

    # Obstacles in display pixels: rectangles (x0, y0, x1, y1) and arrow samples.
    rects = [t.get_window_extent(renderer).extents for t in texts]
    half = MARKER_SIZE / 2 * pt
    for _, _, xy in callouts:
        mx, my = ax.transData.transform(xy)
        rects.append((mx - half, my - half, mx + half, my + half))
    for s, callout, _ in callouts:
        if s.box_xy is not None:
            rects.append(callout.patch.get_window_extent(renderer).extents)
    path_px = [a.get_transform().transform_path(a.get_path()) for a in arrows]
    samples = np.vstack(
        [
            _sample_polyline(poly, step)
            for path in path_px
            for poly in path.to_polygons(closed_only=False)
        ]
    )

    area = ax.get_window_extent(renderer)
    for s, callout, xy in callouts:
        if s.box_xy is not None:
            continue
        frame = callout.patch.get_window_extent(renderer)
        w, h = frame.width, frame.height
        # Offset of the frame's top-left corner from the box_xy anchor point.
        ax0, ay0 = ax.transAxes.transform(callout.xybox)
        dx, dy = frame.x0 - ax0, frame.y1 - ay0

        x0, y1 = np.meshgrid(
            np.arange(area.x0 + clear, area.x1 - clear - w, step),
            np.arange(area.y0 + clear + h, area.y1 - clear, step),
        )
        x0, y1 = x0.ravel(), y1.ravel()
        if x0.size == 0:
            raise ValueError(f"The callout for {s.name} is larger than the map.")
        x1, y0 = x0 + w, y1 - h

        overlap = np.zeros_like(x0)
        for r0, s0, r1, s1 in rects:
            ox = np.minimum(x1, r1 + clear) - np.maximum(x0, r0 - clear)
            oy = np.minimum(y1, s1 + clear) - np.maximum(y0, s0 - clear)
            overlap += np.clip(ox, 0, None) * np.clip(oy, 0, None)
        sx, sy = samples[:, 0], samples[:, 1]
        covered = (
            (sx >= x0[:, None] - clear)
            & (sx <= x1[:, None] + clear)
            & (sy >= y0[:, None] - clear)
            & (sy <= y1[:, None] + clear)
        ).sum(axis=1)
        overlap += covered * step * 2 * clear  # each sample stands for a strip

        mx, my = ax.transData.transform(xy)
        gap = np.hypot(
            np.clip(np.maximum(x0 - mx, mx - x1), 0, None),
            np.clip(np.maximum(y0 - my, my - y1), 0, None),
        )
        best = np.argmin(1000 * overlap + np.abs(gap - leader))

        anchor = (x0[best] - dx, y1[best] - dy)
        callout.xybox = tuple(ax.transAxes.inverted().transform(anchor))
        rects.append((x0[best], y0[best], x1[best], y1[best]))


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
    arrows = []
    for start, end in zip(ROUTE[:-1], ROUTE[1:], strict=True):
        arrows.append(
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
        ax.add_patch(arrows[-1])

    callouts = []
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

        # Grey line: years, role and supervisors, separated by middle dots. The
        # role flows on after the years; a dot that lands at a line break is
        # dropped, since the break already separates.
        details = [
            line.strip(" ·")
            for line in textwrap.wrap(
                f"{s.years}  ·  {s.role}", WRAP_WIDTH, break_on_hyphens=False
            )
        ]
        # The supervisors are kept together: appended to the last line if they
        # fit there, otherwise started on a new line.
        if s.supervisors:
            supervised = f"Supervised by {s.supervisors}"
            if len(details[-1]) + len("  ·  ") + len(supervised) <= WRAP_WIDTH:
                details[-1] += f"  ·  {supervised}"
            else:
                details += textwrap.wrap(supervised, WRAP_WIDTH, break_on_hyphens=False)
        details = "\n".join(details)
        lines = [
            TextArea(
                f"{i}  {s.name}",
                textprops=dict(fontsize=HEADING_SIZE, fontweight="bold", color=INK),
            ),
            TextArea(
                details,
                textprops=dict(fontsize=BODY_SIZE, color="#444444"),
            ),
            TextArea(
                textwrap.fill(s.summary, WRAP_WIDTH, break_on_hyphens=False),
                textprops=dict(fontsize=BODY_SIZE, color=INK),
            ),
        ]
        box = VPacker(
            children=lines,
            align="left",
            pad=0,
            sep=7,
        )
        # Automatic callouts start in the corner; place_callouts moves them.
        callout = AnnotationBbox(
            box,
            xy=(x, y),
            xycoords="data",
            xybox=s.box_xy if s.box_xy is not None else (0.0, 1.0),
            boxcoords="axes fraction",
            box_alignment=(0, 1),
            frameon=True,
            pad=0.6,
            bboxprops=dict(boxstyle="round,pad=0.8", fc="white", ec=s.color, lw=2.6),
            arrowprops=dict(
                arrowstyle="-",
                color=s.color,
                lw=1.8,
                shrinkA=0,
                shrinkB=MARKER_SIZE / 2 + 2,
            ),
            zorder=7,
        )
        ax.add_artist(callout)
        callouts.append((s, callout, (x, y)))

    title_text = fig.text(
        0.03, 0.95, title, fontsize=TITLE_SIZE, fontweight="bold", color=INK, va="top"
    )
    # Anchored to the bottom-right corner of the title, so it follows the title's
    # length and size. Bottoms line up, which matches the baselines as long as
    # both texts have descenders (as "y" in both of them does).
    subtitle_text = ax.annotate(
        subtitle,
        xy=(1, 0),
        xycoords=title_text,
        xytext=(SUBTITLE_SIZE * 1.5, 0),
        textcoords="offset points",
        va="bottom",
        fontsize=SUBTITLE_SIZE,
        fontweight="bold",
        color="#444444",
        annotation_clip=False,
    )
    credit_text = fig.text(
        0.99,
        0.012,
        "Map data: Natural Earth",
        fontsize=CREDIT_SIZE,
        color="#666666",
        ha="right",
    )

    place_callouts(fig, ax, callouts, arrows, [title_text, subtitle_text, credit_text])

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
