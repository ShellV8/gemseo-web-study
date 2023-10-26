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

import tempfile
from os.path import join

import streamlit as st
import streamlit.components.v1 as components
from gemseo import create_design_space
from gemseo import create_scenario
from gemseo import get_available_formulations
from streamlit_tags import st_tags

# this is to keep the widget values between pages
for k, v in st.session_state.items():
    st.session_state[k] = v
st.title("XDSM Generation")

disc_ready = "disciplines" in st.session_state
if disc_ready:
    st.write("Disciplines summary")
    st.dataframe(st.session_state["disciplines_dataframe"], hide_index=True)
    st.divider()

    disciplines = st.session_state["disciplines"]
    all_outputs = set()
    for disc in disciplines:
        all_outputs.update(disc.get_output_data_names())

    all_outputs = list(all_outputs)
    key = "Design variables"
    value = st.session_state.get(key, [])
    design_variables = st_tags(
        label="Design variables",
        text="Press enter to add more",
        suggestions=all_outputs,
        value=value,
        key=key,
    )

    formulations_key = "formulations_list"
    if formulations_key in st.session_state:
        formulations = st.session_state[formulations_key]
    else:
        formulations = get_available_formulations()
        st.session_state[formulations_key] = formulations

    key = "MDO formulation index"
    form = st.session_state.get(key, "MDF")
    index = formulations.index(form)
    formulation = st.selectbox("MDO Formulation", formulations, index=index, key=key)

    key = "maximize_objective"
    maximize_objective = st.checkbox(
        "maximize_objective", value=st.session_state.get(key, False), key=key
    )

    key = "objective"
    index = st.session_state.get(key)
    if index is not None:
        index = all_outputs.index(index)
    objective = st.selectbox(
        "Objective function name", all_outputs, index=index, key=key
    )

    key = "Number of constraints"
    nb_disc = st.slider(
        "Number of constraints",
        min_value=1,
        max_value=20,
        value=st.session_state.get(key, False),
        key=key,
    )

    constraints = {}
    for i in range(nb_disc):
        st.divider()
        constr = st.selectbox(f"Constraint {i + 1}", all_outputs, key=f"constr{i}")
        c_type = st.selectbox(
            "Constraint type",
            ["inequality", "equality"],
            index=0,
            key=f"constr_type{i}",
        )
        if constr:
            constraints[constr] = c_type

    if not (objective and design_variables):
        st.error("Please select an objective and design variables")
    elif st.button("Generate XDSM", type="primary"):
        design_space = create_design_space()
        for name in design_variables:
            design_space.add_variable(name=name)
        try:
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
        except Exception as err:
            st.error(str(err))  # noqa: G200

else:
    st.error("Disciplines are not ready, please check the Disciplines tab")
