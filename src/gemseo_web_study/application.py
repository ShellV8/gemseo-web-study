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

import logging
import tempfile
from os.path import dirname
from os.path import join

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from gemseo import create_design_space
from gemseo import create_scenario
from gemseo import generate_n2_plot
from gemseo import get_available_formulations
from gemseo.problems.scalable.linear.disciplines_generator import (
    create_disciplines_from_desc,
)
from PIL import Image
from streamlit_tags import st_tags


st.set_page_config(page_title="GEMSEO Study", layout="wide")

LOGGER = logging.getLogger(__name__)

st.title("GEMSEO Study analysis and prototyping")

logo = Image.open(join(dirname(__file__), "logo-small.webp"))

st.image(logo, width=300)
nb_disc = st.slider("Number of disciplines", min_value=1, max_value=20, value=2)

disc_desc = []
all_inputs = set()
all_outputs = set()
for i in range(nb_disc):
    st.divider()
    name = st.text_input("Discipline Name", value=f"Discipline{i}", key=f"Disc_{i}")
    inputs = st_tags(
        label=f"Discipline {i} Inputs:",
        text="Press enter to add more",
        value=[],
        key=f"Disc_inputs_{i}",
    )
    outputs = st_tags(
        label=f"Discipline {i} Outputs:",
        text="Press enter to add more",
        value=[],
        key=f"Disc_outputs_{i}",
    )
    disc_desc.append((name, inputs, outputs))
    all_inputs.update(inputs)
    all_outputs.update(outputs)
st.divider()

st.write("Disciplines summary")
try:
    df = pd.DataFrame.from_records(
        [
            {"Name": i[0], "Inputs": str(sorted(i[1])), "Outputs": str(sorted(i[2]))}
            for i in disc_desc
        ],
        columns=["Name", "Inputs", "Outputs"],
    )
    st.dataframe(df, hide_index=True)
    st.divider()
    disciplines = create_disciplines_from_desc(disc_desc)

except ValueError:
    LOGGER.info("Inconsistent disciplines")

if st.button("Generate N2", type="primary"):
    tmpdir = tempfile.mkdtemp()
    tmp_file = join(tmpdir, "n2.png")
    tmp_html = join(tmpdir, "n2.html")

    generate_n2_plot(disciplines, file_path=tmp_file)
    with open(tmp_html, encoding="utf-8") as HtmlFile:  #
        source_code = HtmlFile.read()
        components.html(source_code, width=800, height=800)

st.divider()

st.title("XDSM Generation")
design_variables = st_tags(
    label="Design variables",
    text="Press enter to add more",
    suggestions=list(all_outputs),
    key="desvars",
)

formulations = get_available_formulations()
formulation = st.selectbox(
    "MDO Formulation", formulations, index=formulations.index("MDF")
)
maximize_objective = st.checkbox("maximize_objective", value=False)
objective = st.selectbox("Objective function name", all_outputs, index=None)
nb_disc = st.slider("Number of constraints", min_value=1, max_value=20, value=0)

constraints = {}
for i in range(nb_disc):
    st.divider()
    constr = st.selectbox(f"Constraint {i+1}", all_outputs, key=f"constr{i}")
    c_type = st.selectbox(
        "Constraint type", ["inequality", "equality"], index=0, key=f"constr_type{i}"
    )
    if constr:
        constraints[constr] = c_type

if st.button("Generate XDSM", type="primary"):
    design_space = create_design_space()
    for name in design_variables:
        design_space.add_variable(name=name)
    scenario = create_scenario(
        design_space=design_space,
        objective_name=objective,
        maximize_objective=maximize_objective,
        disciplines=disciplines,
        formulation=formulation,
    )
    cmap = {"inequality": "ineq", "equality": "eq"}
    for constr, ctype in constraints.items():
        scenario.add_constraint(constr, constraint_type=cmap[ctype])
    tmpdir = tempfile.mkdtemp()

    scenario.xdsmize(directory_path=tmpdir)
    tmp_html = join(tmpdir, "xdsm.html")
    with open(tmp_html, encoding="utf-8") as HtmlFile:  #
        source_code = HtmlFile.read()
        components.html(source_code, width=1280, height=1024)
