import dash_core_components as dcc
import dash_bootstrap_components as dbc

extent_opts_card = dbc.Card([
    dbc.CardHeader([
        "erxtent"
    ]),
    dbc.CardBody([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button('Automatic Extent',
                               id='auto_extent_button',
                               color='link'),
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dbc.FormGroup([
                            dbc.Label('Extent modelling area by a factor of'),
                            dcc.Slider(
                                id='calculation_extent',
                                min=1.5,
                                max=5,
                                step=None,
                                marks={
                                    1.5: '1.5x',
                                    3: '3x',
                                    5: '5x',
                                },
                                value=1.5,
                                disabled=True
                            ),
                        ]),
                        dbc.FormGroup([
                            dbc.Label("Determine extent from external DEM"),
                            dbc.InputGroup([
                                dbc.InputGroupAddon(
                                    dbc.Checkbox(
                                        id="standalone-checkbox"
                                    ),
                                    addon_type="prepend"
                                ),
                                dbc.Input(id='targdet_upload_path',
                                          placeholder="e.g., /home/user/mesh_files/mesh.stl",
                                          type="text",
                                          disabled=False),
                            ]),
                            dbc.FormText("Filename must include .stl"),
                        ]),

                    ]),
                    id='auto_extent_collapse',
                    is_open=True
                )
            ]),
            dbc.Card([
                dbc.CardHeader(
                    dbc.Button('Manually Set Extent',
                               id='man_extent_button',
                               color='link'),
                ),
                dbc.Collapse(
                    dbc.CardBody([

                    ]),
                    id='spiral_collapse',
                    is_open=False
                )
            ]),

        ]),
    ]),
])
