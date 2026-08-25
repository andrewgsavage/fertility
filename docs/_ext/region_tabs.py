import pathlib
import sys

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_HFD_SCRIPTS = _REPO_ROOT / "HFD" / "scripts"
if str(_HFD_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_HFD_SCRIPTS))

from country_names import COUNTRY_REGIONS  # noqa: E402


def _slug(name):
    return name.lower().replace(" & ", "_").replace(" / ", "_").replace(" ", "_")


class RegionTabsDirective(SphinxDirective):
    """A tab-item per HFD.scripts.country_names.COUNTRY_REGIONS entry, each
    showing that region's grid image for some per-region chart (built by one
    of the HFD/scripts/*_region_grid.py scripts, named
    "{image_prefix}_{region}.png"). Built live at Sphinx build time so the
    page always matches COUNTRY_REGIONS without any generated markdown being
    written to disk.

    Arguments: the image filename prefix (e.g. "cond_asfr_region"), then the
    alt-text template (the rest of the line, with "{region}" substituted)."""

    has_content = False
    required_arguments = 2
    final_argument_whitespace = True

    def run(self):
        image_prefix, alt_template = self.arguments
        lines = ["::::{tab-set}", ""]
        for region in COUNTRY_REGIONS:
            lines += [
                f":::{{tab-item}} {region}",
                f"```{{image}} /_static/hfd/{image_prefix}_{_slug(region)}.png",
                f":alt: {alt_template.format(region=region)}",
                ":width: 100%",
                "```",
                ":::",
                "",
            ]
        lines.append("::::")
        return self.parse_text_to_nodes("\n".join(lines))


def setup(app: Sphinx):
    app.add_directive("region-tabs", RegionTabsDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
