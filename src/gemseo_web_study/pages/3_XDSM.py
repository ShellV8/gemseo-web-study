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

# this is to keep the widget values between pages
for k, v in st.session_state.items():
    st.session_state[k] = v
st.title("XDSM Generation")
CTYPES = ["inequality", "equality"]

if "disciplines" in st.session_state:
    st.write("Disciplines summary")
    st.dataframe(st.session_state["disciplines_dataframe"], hide_index=True)
    st.divider()

    disciplines = st.session_state["disciplines"]
    all_outputs = st.session_state["all_outputs"]
    all_inputs = st.session_state["all_inputs"]
    key = "Design variables"
    design_variables = st.multiselect(
        "Design variables", options=all_inputs, default=st.session_state.get(key, [])
    )
    st.session_state[key] = design_variables

    formulations_key = "formulations_list"
    if formulations_key in st.session_state:
        formulations = st.session_state[formulations_key]
    else:
        formulations = get_available_formulations()
        st.session_state[formulations_key] = formulations

    key = "MDO formulation index"
    index = st.session_state.get(key, formulations.index("MDF"))
    formulation = st.selectbox(
        "MDO Formulation", formulations, index=index, key="MDO formulation"
    )
    st.session_state[key] = formulations.index(formulation)

    key = "maximize_objective"
    maximize_objective = st.checkbox(
        "maximize_objective", value=st.session_state.get(key, False)
    )
    st.session_state[key] = maximize_objective

    key = "objective_index"
    objective = st.selectbox(
        "Objective function name",
        all_outputs,
        index=st.session_state.get(key, 0),
        key="objective",
    )
    st.session_state[key] = all_outputs.index(objective)

    key = "Number of constraints"
    nb_cstr = st.slider(
        "Number of constraints",
        min_value=0,
        max_value=20,
        value=st.session_state.get(key, 0),
    )
    st.session_state[key] = nb_cstr

    constraints = {}
    for i in range(nb_cstr):
        st.divider()
        key = f"Constraint {i + 1}"
        c_index = st.session_state.get(key)
        constr = st.selectbox(key, all_outputs, index=c_index, key="c_" + key)
        if constr is not None:
            st.session_state[key] = all_outputs.index(constr)

        key = f"constr_type{i}"
        c_type_index = st.session_state.get(key, 0)
        c_type = st.selectbox(
            "Constraint type",
            CTYPES,
            index=c_type_index,
            key="c_" + key,
        )
        if c_type is not None:
            st.session_state[key] = CTYPES.index(c_type)

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
