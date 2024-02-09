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
from gemseo import generate_n2_plot

# this is to keep the widget values between pages
for k, v in st.session_state.items():
    st.session_state[k] = v

disc_ready = "disciplines" in st.session_state
if disc_ready:
    disciplines = st.session_state["disciplines"]

    if st.button("Generate N2", type="primary"):
        tmpdir = tempfile.mkdtemp()
        tmp_file = join(tmpdir, "n2.png")
        tmp_html = join(tmpdir, "n2.html")

        generate_n2_plot(disciplines, file_path=tmp_file)
        with open(tmp_html, encoding="utf-8") as HtmlFile:  #
            source_code = HtmlFile.read()
            components.html(source_code, width=800, height=800)
else:
    st.error("Disciplines are not ready, please check the Disciplines tab.")
