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
from __future__ import annotations

from os.path import dirname
from os.path import join

import streamlit as st
from PIL import Image

st.set_page_config(page_title="GEMSEO Study", layout="wide")


st.title("GEMSEO Study analysis and prototyping")

logo = Image.open(join(dirname(__file__), "logo-small.webp"))

st.image(logo, width=300)

st.markdown(
    """
The GEMSEO Study helps to define the right MDO problem to be
solved before writing any code.

The user only has to define the disciplines by their names,
as well as the input and output names.

Then, the scenario is defined by the names of the objectives, constraints,
design variables, and the selection of the MDO formulation.

The result of the analysis are a N2 and XDSM diagrams.
"""
)
