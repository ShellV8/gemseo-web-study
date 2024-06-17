# noqa: D100 putting a string makes ST fail
# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: Francois Gallard
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

import tempfile
from os.path import join

import streamlit as st
import streamlit.components.v1 as components
from gemseo import MDODiscipline
from gemseo import generate_n2_plot

# this is to keep the widget values between pages
for k, v in st.session_state.items():
    st.session_state[k] = v


@st.cache_data
def generate_html(_disciplines: list[MDODiscipline], disc_desc: list) -> str:
    """Generates the HTML file.

    Args:
        _disciplines: The disciplines instances.
        disc_desc: The disciplines descriptions.
    """
    tmpdir = tempfile.mkdtemp()
    tmp_file = join(tmpdir, "n2.png")
    tmp_html = join(tmpdir, "n2.html")

    generate_n2_plot(_disciplines, file_path=tmp_file)
    with open(tmp_html, encoding="utf-8") as html_file:  #
        return html_file.read()


def handle_n2_genration() -> None:
    """Handles the generation of the N2.

    From the disciplines tab, creates an N2 diagram in the page if the inputs are ready.
    """
    disc_ready = "disciplines" in st.session_state
    if disc_ready:
        disciplines = st.session_state["disciplines"]

        if st.button("Generate N2", type="primary"):
            disc_desc = st.session_state["#disc_desc"]
            source_code = generate_html(disciplines, disc_desc)
            st.download_button(
                "Download N2 standalone HTML file", source_code, file_name="N2.html"
            )
            components.html(source_code, width=800, height=800)

    else:
        st.error("Disciplines are not ready, please check the Disciplines tab.")


# Main display sequence
st.markdown(
    """
The N2 (pronounce "N square") diagram represents the coupling between the disciplines, see: [link]({}).
""".format("https://gemseo.readthedocs.io/en/stable/mdo/coupling.html")
)

handle_n2_genration()
