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

import pandas as pd
import streamlit as st
from gemseo.problems.scalable.linear.disciplines_generator import (
    create_disciplines_from_desc,
)
from streamlit_tags import st_tags

key = "Number of disciplines"
value = st.session_state.get(key, 2)
nb_disc = st.slider(
    "Number of disciplines", min_value=1, max_value=20, value=value, key=key
)

disc_desc = []
for i in range(nb_disc):
    st.divider()
    name = st.text_input("Discipline Name", value=f"Discipline{i}", key=f"Disc_{i}")
    key = f"Disc_inputs_{i}"
    value = st.session_state.get(key, [])
    inputs = st_tags(
        label=f"Discipline {i} Inputs:",
        text="Press enter to add more",
        value=value,
        key=key,
    )

    key = f"Disc_outputs_{i}"
    value = st.session_state.get(key, [])
    outputs = st_tags(
        label=f"Discipline {i} Outputs:",
        text="Press enter to add more",
        value=value,
        key=key,
    )
    disc_desc.append((name, inputs, outputs))

st.divider()
st.write("Disciplines summary")
try:
    if disc_desc is not None:
        df = pd.DataFrame.from_records(
            [
                {
                    "Name": i[0],
                    "Inputs": str(sorted(i[1])),
                    "Outputs": str(sorted(i[2])),
                }
                for i in disc_desc
            ],
            columns=["Name", "Inputs", "Outputs"],
        )
        st.dataframe(df, hide_index=True)
        st.session_state["disciplines_dataframe"] = df
        st.divider()
        disciplines = create_disciplines_from_desc(disc_desc)
        st.session_state["disciplines"] = disciplines
        all_outputs = set()
        all_inputs = set()
        for disc in disciplines:
            all_outputs.update(disc.get_output_data_names())
            all_inputs.update(disc.get_input_data_names())
        st.session_state["all_outputs"] = sorted(all_outputs)
        st.session_state["all_inputs"] = sorted(all_inputs)

except (ValueError, TypeError):
    if "disciplines" in st.session_state:
        del st.session_state["disciplines"]
