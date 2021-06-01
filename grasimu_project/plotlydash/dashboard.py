"""Instantiate a Dash app."""
import json
import pandas as pd
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from ..constructors import Scene
from plotly.subplots import make_subplots
import plotly.express as px

from .ui_top import sidebar, content_style
from .ui_target import target_layout
from .ui_terrain import terrain_layout
from .ui_survey import survey_layout
from .ui_vis import vis_layout


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=False,
    )

    content = html.Div(id="page-content", style=content_style)
    dash_app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

    # this callback uses the current pathname to set the active state of the
    # corresponding nav link to true, allowing users to see what page they are on.
    @dash_app.callback(
        [Output(f"page-{i}-link", "active") for i in range(1, 4)],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/dashapp/":
            # Treat page 1 as the homepage / index
            return True, False, False
        return [pathname == f"/dashapp/page-{i}" for i in range(1, 4)]

    sc = Scene('scene1')

    @dash_app.callback([Output('target_mesh_plot', 'figure'),
                        Output('voxel_button', 'disabled'),
                        Output('voxel_button_text', 'children')],
                       Input('target_render_button', 'n_clicks'),
                       [State('target_upload_path', 'value'),
                        State('target_geometry_radio', 'value'),
                        State('radius_comp_input', 'value'),
                        State('length_comp_input', 'value'),
                        State('cen_x_input', 'value'),
                        State('cen_y_input', 'value'),
                        State('cen_z_input', 'value')],
                       prevent_initial_call=True)
    def render_mesh(click, path, mode, radius, length, x0, y0, z0):
        voxel_button_status = True
        voxel_button_text = "No mesh in memory."

        if mode == 'custom':
            file_path = path
            target_shape = None
        else:
            file_path = None
            target_shape = mode

        sc.render_mesh(centre_depth=z0,
                       centre_x=x0,
                       centre_y=y0,
                       path=file_path,
                       shape=target_shape,
                       radius=radius,
                       length=length)

        if click > 0:
            voxel_button_status = False
            voxel_button_text = "Click to voxelize the mesh displayed in the 3D Mesh Plot."

        mesh_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['mesh']['vertices'][:, 0],
                                            y=sc.target_geometry['mesh']['vertices'][:, 1],
                                            z=sc.target_geometry['mesh']['vertices'][:, 2],
                                            i=sc.target_geometry['mesh']['indices'][:, 0],
                                            j=sc.target_geometry['mesh']['indices'][:, 1],
                                            k=sc.target_geometry['mesh']['indices'][:, 2]))

        mesh_fig.update_scenes(aspectmode='data')

        return mesh_fig, voxel_button_status, voxel_button_text

    @dash_app.callback([Output('target_voxel_plot', 'figure'),
                        Output('gravity_button', 'disabled'),
                        Output('gravity_button_text', 'children')],
                       Input('voxel_button', 'n_clicks'),
                       State('voxel_resolution_input', 'value'),
                       prevent_initial_call=True)
    def voxelize_mesh(click, resolution):
        gravity_button_status = True
        gravity_button_text = "No voxel model in memory."

        sc.voxelize_mesh(resolution=resolution)

        vox_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                           y=sc.target_geometry['voxel']['vertices'][:, 1],
                                           z=sc.target_geometry['voxel']['vertices'][:, 2],
                                           i=sc.target_geometry['voxel']['indices'][:, 0],
                                           j=sc.target_geometry['voxel']['indices'][:, 1],
                                           k=sc.target_geometry['voxel']['indices'][:, 2]))

        vox_fig.add_trace(go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                       y=sc.target_geometry['wireframe'][1],
                                       z=sc.target_geometry['wireframe'][2],
                                       mode='lines',
                                       line=dict(color='rgb(70,70,70)', width=1)))

        vox_fig.update_scenes(aspectmode='data')

        if click > 0:
            gravity_button_status = False
            gravity_button_text = "Click to calculate gravity at z=0"

        return vox_fig, gravity_button_status, gravity_button_text

    @dash_app.callback([Output(f'{i}_collapse', 'is_open') for i in ['auto_extent', 'manual_extent']],
                       [Input(f'{i}_button', 'n_clicks') for i in ['auto_extent', 'manual_extent']],
                       [State(f'{i}_collapse', 'is_open') for i in ['auto_extent', 'manual_extent']],
                       prevent_initial_call=True)
    def extent_collapse(n1, n2, is_open1, is_open2):
        ctx = dash.callback_context

        if not ctx.triggered:
            return False, False
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "auto_extent_button" and n1:
            return not is_open1, False
        elif button_id == "manual_extent_button" and n2:
            return False, not is_open2
        return False, False

    @dash_app.callback([Output('calculation_extent', 'disabled'),
                        Output('extent_dem_path', 'disabled'),
                        Output('extent_dem_resolution', 'disabled')],
                       Input('extent_dem_checkbox', 'checked'))
    def toggle_extent_slider(use_dem):
        if use_dem:
            slider_status = True
            path_status = False
            res_status = False
        else:
            slider_status = False
            path_status = True
            res_status = True
        return slider_status, path_status, res_status

    # @dash_app.callback(Output('target_tab_2', 'disabled'),
    #                    Input('target_geometry_radio', 'value'))
    # def toggle_target_tab(use_geom):
    #     if use_geom is 'sphere':
    #         tab_status = False
    #     else:
    #         tab_status = True
    #     return tab_status

    @dash_app.callback(Output('extent_pick_plot', 'figure'),
                       Input('extent_button', 'n_clicks'),
                       [State('calculation_resolution_input', 'value'),
                        State('calculation_extent', 'value'),
                        State('extent_x1_input', 'value'),
                        State('extent_y1_input', 'value'),
                        State('extent_x2_input', 'value'),
                        State('extent_y2_input', 'value'),
                        State('auto_extent_collapse', 'is_open'),
                        State('extent_dem_checkbox', 'checked'),
                        State('extent_dem_path', 'value'),
                        State('extent_dem_resolution', 'value')],
                       prevent_initial_call=True)
    def plot_extent(click, resolution, extent_multiplier, extent_x1, extent_y1, extent_x2, extent_y2,
                    auto_is_open, use_dem, path, dem_res):
        ctx = dash.callback_context

        if auto_is_open:
            if use_dem:
                use_path = path
                extent_multiplier = None
                # resolution currently needs to be an integer
            else:
                use_path = None
                dem_res = None
        else:
            use_path = None
            dem_res = None
            extent_multiplier = None

        sc.create_datum(resolution=resolution,
                        extent_multiplier=extent_multiplier,
                        extent_x1=extent_x1, extent_y1=extent_y1,
                        extent_x2=extent_x2, extent_y2=extent_y2,
                        path=use_path, dem_res=dem_res)
        x = np.arange(sc.scene_properties['scene_bounds'][0], sc.scene_properties['scene_bounds'][2] + 1)
        y = np.arange(sc.scene_properties['scene_bounds'][1], sc.scene_properties['scene_bounds'][3] + 1)
        xx, yy = np.meshgrid(x, y)
        z = np.ones_like(xx) * 0.3
        # z[::2, ::2] = 0.2
        # z[1::2, 1::2] = 0.4

        # z = sc.data['elevation']['terrain'][3]

        x_vals = sc.scene_properties['datum'][0].ravel()
        y_vals = sc.scene_properties['datum'][1].ravel()

        extent_fig = go.Figure(go.Scatter(x=x_vals,
                                        y=y_vals, mode='markers',
                                        marker_color='blue', showlegend=True,
                                        marker_size=3, name='Station'))
        extent_fig.add_shape(type="rect",
                             x0=sc.scene_properties['scene_bounds'][0],
                             y0=sc.scene_properties['scene_bounds'][1],
                             x1=sc.scene_properties['scene_bounds'][2],
                             y1=sc.scene_properties['scene_bounds'][3],
                             line=dict(
                                 color="RoyalBlue",
                                 width=1),
                             )
        # extent_fig.add_trace()

        extent_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                 xaxis=dict(scaleanchor='y'))
        return extent_fig

    @dash_app.callback(Output('target_grav_plot', 'figure'),
                       [Input('gravity_button', 'n_clicks'),
                        Input('target_tabs', 'active_tab')],
                       [State('density_input', 'value')],
                       prevent_initial_call=True)
    def plot_perfect_gravity(click, tab, density):
        ctx = dash.callback_context

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'target_tabs':
            return None
        elif ctx.triggered[0]['prop_id'].split('.')[0] == 'gravity_button':
            sc.calculate_target_gravity(density_contrast=density, with_terrain=False)
            sc.calculate_analytical_sphere(rho=density)
        num_attrs = dict(x=sc.data['perfect_gravity']['target'][0],
                         y=sc.data['perfect_gravity']['target'][1],
                         z=sc.data['perfect_gravity']['target'][2],
                         colorbar_title="milligals")
        ana_attrs = dict(x=sc.data['perfect_gravity']['ana'][0],
                         y=sc.data['perfect_gravity']['ana'][1],
                         z=sc.data['perfect_gravity']['ana'][2],
                         colorbar_title="milligals")
        if tab == 'target_tab_2':
            fig_data = go.Heatmap(ana_attrs)
        elif tab == 'target_tab_1':
            fig_data = go.Heatmap(num_attrs)

        perfect_fig = go.Figure(fig_data)
        perfect_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                  xaxis=dict(scaleanchor='y'))

        return perfect_fig

    @dash_app.callback([Output('terrain_plot', 'figure'),
                        Output('dem_button', 'disabled'),
                        Output('dem_button_text', 'children')],
                       [Input('terrain_button', 'n_clicks'),
                        Input('terrain_tabs', 'active_tab'),
                        Input('cmap_holder', 'children')],
                       [State('seed_input', 'value'),
                        State('corr_x_input', 'value'),
                        State('corr_y_input', 'value'),
                        State('max_input', 'value'),
                        State('min_input', 'value'),
                        State('terrain_upload_path', 'value'),
                        State('terrain_dropdown', 'value')],
                       prevent_initial_call=True)
    def plot_terrain(click, tab, cmap_dump, seed, corr_x, corr_y, max_in, min_in, path, method):
        ctx = dash.callback_context
        if method == 6:
            path_status = False
        else:
            path_status = True

        dem_button_status = False
        dem_button_text = "No terrain surface in memory."
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'terrain_button':
            sc.generate_terrain(seed=seed,
                                method=method,
                                x_corr_len=corr_x,
                                y_corr_len=corr_y,
                                max_elevation=max_in, min_elevation=min_in,
                                path=path)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'terrain_tabs':
            return None, None, None
        else:
            if cmap_dump:
                cmap_load = json.loads(cmap_dump)
                zmin = cmap_load[0]
                zmax = cmap_load[1]
            else:
                zmin = np.min(sc.data['elevation']['terrain'][2])
                zmax = np.max(sc.data['elevation']['terrain'][2])

            dem_button_status = False
            dem_button_text = "Click to generate DTM surface."
            raster_attrs = dict(x=sc.data['elevation']['terrain'][0],
                                y=sc.data['elevation']['terrain'][1],
                                z=sc.data['elevation']['terrain'][2],
                                colorbar_title="metres",
                                colorscale='Viridis',
                                zmin=zmin, zmax=zmax)
            surface_attrs = dict(x=sc.scene_properties['datum'][0],
                                 y=sc.scene_properties['datum'][1],
                                 z=sc.data['elevation']['terrain'][3],
                                 colorbar_title="metres",
                                 colorscale='Viridis',
                                 cmin=zmin, cmax=zmax)

            if tab == 'terrain_tab_2':
                fig_data = go.Heatmap(raster_attrs)
            elif tab == 'terrain_tab_1':
                fig_data = go.Surface(surface_attrs)
                vox_data = [go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                      y=sc.target_geometry['voxel']['vertices'][:, 1],
                                      z=sc.target_geometry['voxel']['vertices'][:, 2],
                                      i=sc.target_geometry['voxel']['indices'][:, 0],
                                      j=sc.target_geometry['voxel']['indices'][:, 1],
                                      k=sc.target_geometry['voxel']['indices'][:, 2],
                                      color='rgb(77,81,255)'),
                            go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                         y=sc.target_geometry['wireframe'][1],
                                         z=sc.target_geometry['wireframe'][2],
                                         mode='lines',
                                         line=dict(color='rgb(70,70,70)', width=1))]

            terrain_fig = go.Figure(fig_data)
            terrain_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                      xaxis=dict(scaleanchor='y'))
            if tab == 'terrain_tab_1':
                terrain_fig.add_trace(vox_data[0])
                terrain_fig.add_trace(vox_data[1])
                terrain_fig.update_scenes(aspectmode='data')

            print(sc.data['elevation']['terrain'][2])

            return terrain_fig, dem_button_status, dem_button_text

    @dash_app.callback([Output('dem_plot', 'figure'),
                        Output('cmap_holder', 'children'),
                        Output('tgrav_button', 'disabled'),
                        Output('tgrav_button_text', 'children')],
                       [Input('dem_button', 'n_clicks'),
                        Input('dem_tabs', 'active_tab')],
                       [State('dem_input', 'value')],
                       prevent_initial_call=True)
    def plot_dem(click, tab, dem_err):
        ctx = dash.callback_context
        tgrav_button_status = True
        tgrav_button_text = "No DTM in memory."
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'dem_button':
            sc.generate_dem(err=dem_err)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'dem_tabs':
            return None, None, None, None
        else:
            tgrav_button_status = False
            tgrav_button_text = "Click to calculate gravitational acceleration for true terrain and DTM."
            raster_attrs = dict(x=sc.data['elevation']['dem'][0],
                                y=sc.data['elevation']['dem'][1],
                                z=sc.data['elevation']['dem'][2],
                                colorbar_title="metres",
                                colorscale='Viridis')
            surface_attrs = dict(x=sc.scene_properties['datum'][0],
                                 y=sc.scene_properties['datum'][1],
                                 z=sc.data['elevation']['dem'][3],
                                 colorbar_title="metres",
                                 colorscale='Viridis')

            if tab == 'dem_tab_2':
                fig_data = go.Heatmap(raster_attrs)
            elif tab == 'dem_tab_1':
                fig_data = go.Surface(surface_attrs)
                vox_data = [go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                      y=sc.target_geometry['voxel']['vertices'][:, 1],
                                      z=sc.target_geometry['voxel']['vertices'][:, 2],
                                      i=sc.target_geometry['voxel']['indices'][:, 0],
                                      j=sc.target_geometry['voxel']['indices'][:, 1],
                                      k=sc.target_geometry['voxel']['indices'][:, 2],
                                      color='rgb(77,81,255)'),
                            go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                         y=sc.target_geometry['wireframe'][1],
                                         z=sc.target_geometry['wireframe'][2],
                                         mode='lines',
                                         line=dict(color='rgb(70,70,70)', width=1))]

            dem_fig = go.Figure(fig_data)
            dem_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                  xaxis=dict(scaleanchor='y'))
            if tab == 'dem_tab_1':
                dem_fig.add_trace(vox_data[0])
                dem_fig.add_trace(vox_data[1])
                dem_fig.update_scenes(aspectmode='data')

            zmin = np.min(sc.data['elevation']['dem'][2])
            zmax = np.max(sc.data['elevation']['dem'][2])

            cmap_dump = json.dumps([zmin, zmax])

            return dem_fig, cmap_dump, tgrav_button_status, tgrav_button_text

    @dash_app.callback(Output('tgrav_plot', 'figure'),
                       [Input('tgrav_button', 'n_clicks'),
                        Input('tgrav_tabs', 'active_tab')],
                       State('t_density_input', 'value'),
                       prevent_initial_call=True)
    def plot_terrain_gravity(click, tab, density):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'tgrav_button':
            sc.calculate_terrain_gravity(rho=density)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'tgrav_tabs':
            return None, None, None
        else:
            dem_attrs = dict(x=sc.data['perfect_gravity']['dem'][0],
                             y=sc.data['perfect_gravity']['dem'][1],
                             z=sc.data['perfect_gravity']['dem'][2],
                             colorbar_title="milligals")
            gt_attrs = dict(x=sc.data['perfect_gravity']['terrain'][0],
                            y=sc.data['perfect_gravity']['terrain'][1],
                            z=sc.data['perfect_gravity']['terrain'][2],
                            colorbar_title="milligals")
        if tab == 'tgrav_tab_2':
            fig_data = go.Heatmap(dem_attrs)
        elif tab == 'tgrav_tab_1':
            fig_data = go.Heatmap(gt_attrs)

        tgrav_fig = go.Figure(fig_data)
        tgrav_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                xaxis=dict(scaleanchor='y'))

        return tgrav_fig

    @dash_app.callback([Output(f'{i}_collapse', 'is_open') for i in ['grid', 'spiral', 'points']],
                       [Input(f'{i}_display_button', 'n_clicks') for i in ['grid', 'spiral', 'points']],
                       [State(f'{i}_collapse', 'is_open') for i in ['grid', 'spiral', 'points']],
                       prevent_initial_call=True)
    def survey_collapse(n1, n2, n3, is_open1, is_open2, is_open3):
        ctx = dash.callback_context

        if not ctx.triggered:
            return False, False, False
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "grid_display_button" and n1:
            return not is_open1, False, False
        elif button_id == "spiral_display_button" and n2:
            return False, not is_open2, False
        elif button_id == "points_display_button" and n3:
            return False, False, not is_open3
        return False, False, False

    @dash_app.callback(Output('survey_plot', 'figure'),
                       [Input('simulate_button', 'n_clicks'),
                        Input('survey_tabs', 'active_tab')],
                       [State('grav_err_input', 'value'),
                        State('gps_err_input', 'value')],
                       prevent_initial_call=True)
    def plot_survey(click, tab, grav_err, gps_err):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'simulate_button':
            sc.calculate_target_gravity(sc.target_parameters['density'],
                                        with_terrain=True,
                                        with_noise=True,
                                        grav_err=grav_err, gps_err=gps_err)
            sc.calculate_target_gravity(sc.target_parameters['density'],
                                        with_terrain=False,
                                        with_noise=True,
                                        grav_err=grav_err, gps_err=gps_err)
            sc.calculate_target_gravity(sc.target_parameters['density'],
                                        with_terrain=True,
                                        with_noise=False,
                                        grav_err=grav_err, gps_err=gps_err)
        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'survey_tabs':
            return None, None, None
        else:
            full_attrs = dict(x=sc.data['noisy_gravity']['full'][0],
                              y=sc.data['noisy_gravity']['full'][1],
                              z=sc.data['noisy_gravity']['full'][2],
                              colorbar_title="milligals")
            nt_attrs = dict(x=sc.data['noisy_gravity']['target'][0],
                            y=sc.data['noisy_gravity']['target'][1],
                            z=sc.data['noisy_gravity']['target'][2],
                            colorbar_title="milligals")
        if tab == 'survey_tab_1':
            fig_data = go.Heatmap(full_attrs)
        elif tab == 'survey_tab_2':
            fig_data = go.Heatmap(nt_attrs)

        survey_fig = go.Figure(fig_data)
        survey_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                 xaxis=dict(scaleanchor='y'))

        return survey_fig

    @dash_app.callback([Output('survey_pick_plot', 'figure'),
                        Output('interp_button', 'disabled'),
                        Output('interp_button_text', 'children')],
                       Input('survey_table', 'data'),
                       [State('count_data', 'children')])
    def pick_survey(data, count):
        ctx = dash.callback_context
        interp_button_status = True
        interp_button_text = 'Not enough survey points in memory (at least 3 required).'
        try:
            survey_pick_fig = go.Figure(data=go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                                       y=sc.target_geometry['voxel']['vertices'][:, 1],
                                                       z=sc.target_geometry['voxel']['vertices'][:, 2],
                                                       i=sc.target_geometry['voxel']['indices'][:, 0],
                                                       j=sc.target_geometry['voxel']['indices'][:, 1],
                                                       k=sc.target_geometry['voxel']['indices'][:, 2]))
            survey_pick_fig.add_trace(go.Surface(x=(sc.scene_properties['datum'][0]),
                                                 y=sc.scene_properties['datum'][1],
                                                 z=sc.scene_properties['datum'][2],
                                                 showscale=False,
                                                 opacity=0.2))
            survey_pick_fig.update_scenes(aspectmode='data',
                                          dragmode=False)
            survey_pick_fig.update_layout(scene_camera=dict(eye=dict(x=0., y=0., z=2)))

        except TypeError:
            print("No target or terrain data loaded.")
            return go.Figure(), interp_button_status, interp_button_text

        if ctx.triggered[0]['prop_id'].split('.')[0] == 'survey_table':
            count = int(count) - 1
            x_vals = [float(data[c]['column_1']) for c in range(count + 1)]
            y_vals = [float(data[c]['column_2']) for c in range(count + 1)]
            z_vals = [float(data[c]['column_3']) for c in range(count + 1)]

            survey_pick_fig.add_trace(go.Scatter3d(x=x_vals,
                                                   y=y_vals,
                                                   z=z_vals,
                                                   mode='markers',
                                                   marker_color='white',
                                                   marker_size=2))

            if count > 1:
                interp_button_status = False
                interp_button_text = "Click to interpolate between survey points."

        return survey_pick_fig, interp_button_status, interp_button_text

    @dash_app.callback(Output('interp_plot', 'figure'),
                       [Input('interp_button', 'n_clicks'),
                        Input('interp_tabs', 'active_tab')],
                       [State('grav_err_input', 'value'),
                        State('gps_err_input', 'value'),
                        State('survey_table', 'data'),
                        State('count_data', 'children'),
                        State('sip_radio', 'value')],
                       prevent_initial_call=True)
    def plot_interpolated_survey(click, tab, grav_err, gps_err, data, count, method):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'interp_button':
            count = int(count) - 1
            x_vals = [float(data[c]['column_1']) for c in range(count + 1)]
            y_vals = [float(data[c]['column_2']) for c in range(count + 1)]
            z_vals = [float(data[c]['column_3']) for c in range(count + 1)]

            sc.update_survey(x_vals, y_vals, z_vals, grav_err, gps_err)
            sc.interpolate_survey_pts(method=method)

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'interp_tabs':
            return None, None, None
        else:
            interp_attrs = dict(x=sc.data['interp_gravity']['raw'][0],
                                y=sc.data['interp_gravity']['raw'][1],
                                z=sc.data['interp_gravity']['raw'][2],
                                colorbar_title="milligals")
            perfect_attrs = dict(x=sc.data['interp_gravity']['target'][0],
                                 y=sc.data['interp_gravity']['target'][1],
                                 z=sc.data['interp_gravity']['target'][2],
                                 colorbar_title="milligals")
        if tab == 'interp_tab_2':
            fig_data = go.Heatmap(perfect_attrs)
        elif tab == 'interp_tab_1':
            fig_data = go.Heatmap(interp_attrs)

        interp_fig = go.Figure(fig_data)
        interp_fig.update_layout(yaxis=dict(scaleanchor='x'),
                                 xaxis=dict(scaleanchor='y'))

        return interp_fig

    @dash_app.callback(Output('click_data', 'children'),
                       [Input('survey_pick_plot', 'clickData')],
                       prevent_initial_call=True)
    def collect_click_data(click_data):
        x_pos = click_data['points'][0]['x']
        y_pos = click_data['points'][0]['y']
        z_pos = click_data['points'][0]['z']
        pos = [x_pos, y_pos, z_pos]
        return json.dumps(pos, indent=2)

    # @dash_app.callback([Output('grid_plot', 'figure'),],
    #                    [Input('grid_plot', 'selectedData')],
    #                    prevent_initial_call=True)
    # def grid_builder(click_data):

    # comment
    @dash_app.callback([Output('survey_table', 'data'),
                        Output('count_data', 'children')],
                       [Input('click_data', 'children'),
                        Input('new_survey_button', 'n_clicks')],
                       [State('survey_table', 'data'),
                        State('survey_table', 'columns')],
                       prevent_initial_call=True)
    def update_table(pos, click, table_data, table_cols):
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'click_data':
            data = json.loads(pos)
            table_data.append({c['id']: data[i] for c, i in zip(table_cols, range(0, 3))})
            count = len(table_data)
        elif ctx.triggered[0]['prop_id'].split('.')[0] == 'new_survey_button':
            table_data = list()
            count = 0
        return table_data, count

    # Target Geometry active/inactive fields callback
    @dash_app.callback([Output('radius_comp_input', 'disabled'),
                        Output('length_comp_input', 'disabled'),
                        Output('target_upload_path', 'disabled'),
                        Output('tt2', 'disabled')],
                       Input('target_geometry_radio', 'value'),
                       prevent_initial_call=False)
    def geom_field_status(selection):
        status = [True, True, True, True]
        if selection == 'sphere':
            status[0] = False
            tab_status = False
        elif selection == 'cylinder':
            status[0] = False
            status[1] = False
            tab_status = True
        elif selection == 'custom':
            status[2] = False
            tab_status = True
        return status[0], status[1], status[2], tab_status

    # Terrain active/inactive fields callback
    @dash_app.callback([Output('seed_input', 'disabled'),
                        Output('corr_x_input', 'disabled'),
                        Output('corr_y_input', 'disabled'),
                        Output('max_input', 'disabled'),
                        Output('min_input', 'disabled'),
                        Output('terrain_upload_path', 'disabled')],
                       Input('terrain_dropdown', 'value'),
                       prevent_initial_call=False)
    def geom_field_status(selection):
        if selection == 6:
            seed_status = True
            corr_x_status = True
            corr_y_status = True
            max_status = True
            min_status = True
            path_status = False
        elif selection == 1:
            seed_status = False
            corr_x_status = False
            corr_y_status = True
            max_status = False
            min_status = False
            path_status = True
        else:
            seed_status = False
            corr_x_status = False
            corr_y_status = False
            max_status = False
            min_status = False
            path_status = True

        return seed_status, corr_x_status, corr_y_status, max_status, min_status, path_status

    @dash_app.callback([Output('vis_target_plot', 'figure'),
                        Output('vis_full_plot', 'figure'),
                        Output('vis_raw_plot', 'figure'),
                        Output('vis_slice_plot', 'figure')],
                       [Input('vis_button', 'n_clicks'),
                        Input('vis_click_data', 'children'),
                        Input('vis_slice_dropdown', 'value'),
                        Input('correction_radio', 'value'),
                        Input('vis_tabs', 'active_tab')],
                       prevent_initial_call=True)
    def vis(click, pos, value, correction, tab):
        ctx = dash.callback_context
        if correction == [0, 1] or correction == [1, 0]:
            sc.apply_corrections(free_air=True, terrain=True)
        elif correction == [0]:
            sc.apply_corrections(free_air=True, terrain=False)
        elif correction == [1]:
            sc.apply_corrections(free_air=False, terrain=True)
        else:
            sc.apply_corrections(free_air=False, terrain=False)

        selected_plot_list = [sc.data['interp_gravity']['target'],
                              sc.data['interp_gravity']['full'],
                              sc.data['interp_gravity']['raw'],
                              sc.data['perfect_gravity']['target'],
                              sc.data['perfect_gravity']['full'],
                              sc.data['noisy_gravity']['full'],
                              sc.data['perfect_gravity']['terrain'],
                              sc.data['perfect_gravity']['dem'],
                              sc.corrections['free_air'],
                              sc.corrections['terrain'],
                              sc.data['elevation']['terrain'],
                              sc.data['elevation']['dem'],
                              sc.data['corrected_gravity']['full'],
                              sc.data['corrected_gravity']['interp']]

        if value == 10 or value == 11:
            unit = 'metres'
        else:
            unit = 'milligals'

        if click is None and ctx.triggered[0]['prop_id'].split('.')[0] == 'vis_tabs':
            return None, None, None, None
        else:
            if tab == 'vis_tab_1':
                data = [selected_plot_list[0][3],
                        selected_plot_list[1][3],
                        selected_plot_list[13][3]]
            elif tab == 'vis_tab_2':
                data = [selected_plot_list[3][3],
                        selected_plot_list[4][3],
                        selected_plot_list[12][3]]

        c1_fig = px.imshow(img=np.flipud(data[0]),
                           x=sc.scene_properties['datum'][0][0, :],
                           y=sc.scene_properties['datum'][1][:, 0])

        c1_fig.update_layout(coloraxis_colorbar=dict(title='milligal'))

        c2_fig = px.imshow(img=np.flipud(data[1]),
                           x=sc.scene_properties['datum'][0][0, :],
                           y=sc.scene_properties['datum'][1][:, 0])

        c2_fig.update_layout(coloraxis_colorbar=dict(title='milligal'))

        c3_fig = px.imshow(img=np.flipud(data[2]),
                           x=sc.scene_properties['datum'][0][0, :],
                           y=sc.scene_properties['datum'][1][:, 0])

        c3_fig.update_layout(coloraxis_colorbar=dict(title='milligal'))

        slice_fig = px.imshow(img=np.flipud(selected_plot_list[value][3]),
                              x=sc.scene_properties['datum'][0][0, :],
                              y=sc.scene_properties['datum'][1][:, 0])
        slice_fig.update_xaxes(spikemode='across', showspikes=True)
        slice_fig.update_yaxes(spikemode='across', showspikes=True)

        if ctx.triggered[0]['prop_id'].split('.')[0] == 'vis_click_data':
            click_data = json.loads(pos)
            x_pos = click_data[0]
            y_pos = click_data[1]

            x_trace = go.Scatter(x=sc.scene_properties['datum'][0][0, :],
                                 y=np.ones_like(sc.scene_properties['datum'][0][0, :]) * y_pos,
                                 marker_color='cyan',
                                 name="E-W")
            y_trace = go.Scatter(x=np.ones_like(sc.scene_properties['datum'][1][0, :]) * x_pos,
                                 y=sc.scene_properties['datum'][1][:, 0],
                                 marker_color='lightgreen',
                                 name="N-S")

            slice_fig.add_trace(x_trace)
            slice_fig.add_trace(y_trace)
            slice_fig.update_layout(legend_title=unit)

        return c1_fig, c2_fig, c3_fig, slice_fig

    @dash_app.callback([Output('vis_table', 'children'),
                        Output('vis_3d_plot', 'figure')],
                       [Input('vis_target_plot', 'figure'),
                        Input('sum_tabs', 'active_tab')])
    def vis_summary(click, tab):
        sim_df = pd.DataFrame(list(zip(sc.sim_params.keys(), sc.sim_params.values())),
                              columns=['Parameter', 'Value'])

        param_table = dbc.Table.from_dataframe(sim_df)

        terrain_data = go.Surface(x=sc.scene_properties['datum'][0],
                                  y=sc.scene_properties['datum'][1],
                                  z=sc.data['elevation']['terrain'][3],
                                  colorbar_title="metres",
                                  colorscale='Viridis')

        if tab == 'sum_tab_1':
            fig = go.Figure(terrain_data)
            fig.add_trace(go.Mesh3d(x=sc.target_geometry['mesh']['vertices'][:, 0],
                                    y=sc.target_geometry['mesh']['vertices'][:, 1],
                                    z=sc.target_geometry['mesh']['vertices'][:, 2],
                                    i=sc.target_geometry['mesh']['indices'][:, 0],
                                    j=sc.target_geometry['mesh']['indices'][:, 1],
                                    k=sc.target_geometry['mesh']['indices'][:, 2],
                                    color='rgb(77,81,255)'))
        elif tab == 'sum_tab_2':
            fig = go.Figure(terrain_data)
            fig.add_trace(go.Mesh3d(x=sc.target_geometry['voxel']['vertices'][:, 0],
                                    y=sc.target_geometry['voxel']['vertices'][:, 1],
                                    z=sc.target_geometry['voxel']['vertices'][:, 2],
                                    i=sc.target_geometry['voxel']['indices'][:, 0],
                                    j=sc.target_geometry['voxel']['indices'][:, 1],
                                    k=sc.target_geometry['voxel']['indices'][:, 2],
                                    color='rgb(77,81,255)'))
            fig.add_trace(go.Scatter3d(x=sc.target_geometry['wireframe'][0],
                                       y=sc.target_geometry['wireframe'][1],
                                       z=sc.target_geometry['wireframe'][2],
                                       mode='lines',
                                       line=dict(color='rgb(70,70,70)', width=1)))
        return param_table, fig

    @dash_app.callback(Output('vis_xy_plot', 'figure'),
                       [Input('vis_click_data', 'children'),
                        Input('vis_target_toggle', 'value')],
                       State('vis_slice_dropdown', 'value'),
                       prevent_initial_call=True)
    def vis_slice(pos, toggle, value):
        selected_plot_list = [sc.data['interp_gravity']['target'],
                              sc.data['interp_gravity']['full'],
                              sc.data['interp_gravity']['raw'],
                              sc.data['perfect_gravity']['target'],
                              sc.data['perfect_gravity']['full'],
                              sc.data['noisy_gravity']['full'],
                              sc.data['perfect_gravity']['terrain'],
                              sc.data['perfect_gravity']['dem'],
                              sc.corrections['free_air'],
                              sc.corrections['terrain'],
                              sc.data['elevation']['terrain'],
                              sc.data['elevation']['dem'],
                              sc.data['corrected_gravity']['full'],
                              sc.data['corrected_gravity']['interp']]

        if value == 10 or value == 11:
            unit = 'metres'
        else:
            unit = 'milligals'

        click_data = json.loads(pos)
        x_pos = click_data[0]
        y_pos = click_data[1]

        idx = np.where(sc.scene_properties['datum'][0] == x_pos)[1][0]
        idy = np.where(sc.scene_properties['datum'][1] == y_pos)[0][0]

        y_min = np.min(np.flipud(selected_plot_list[value][3]))
        y_max = np.max(np.flipud(selected_plot_list[value][3]))

        fig = make_subplots(rows=2, cols=1,
                            shared_xaxes=True,
                            x_title='Position, metres',
                            y_title='Signal Strength, ' + unit)

        fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[value][3])[idy, :],
                                    x=sc.scene_properties['datum'][0][idx, :],
                                    name='E-W', marker_color='cyan'),
                         row=1, col=1)
        fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[value][3])[:, idx],
                                    x=sc.scene_properties['datum'][1][:, idx],
                                    name='N-S', marker_color='lightgreen'),
                         row=2, col=1)

        if toggle == [0] and (value not in range(8, 11)):
            fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[3][3])[idy, :],
                                        x=sc.scene_properties['datum'][0][idx, :],
                                        name='Target', marker_color='red'),
                             row=1, col=1)
            fig.append_trace(go.Scatter(y=np.flipud(selected_plot_list[3][3])[:, idx],
                                        x=sc.scene_properties['datum'][1][:, idx],
                                        name='Target', marker_color='red', showlegend=False),
                             row=2, col=1)

        fig.update_yaxes(range=[y_min, y_max])

        return fig

    @dash_app.callback(Output('vis_click_data', 'children'),
                       Input('vis_slice_plot', 'clickData'),
                       prevent_initial_call=True)
    def vis_get_click(click_data):
        x_pos = click_data['points'][0]['x']
        y_pos = click_data['points'][0]['y']
        pos = [x_pos, y_pos]
        return json.dumps(pos)

    @dash_app.callback(Output("vis_collapse", "is_open"),
                       [Input("vis_3d_button", "n_clicks")],
                       [State("vis_collapse", "is_open")],
                       prevent_initial_call=True)
    def toggle_vis_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @dash_app.callback(Output('vis_download_modal', 'is_open'),
                       [Input('vis_dl_button', 'n_clicks'),
                        Input('vis_close_button', 'n_clicks')],
                       [State('vis_download_modal', 'is_open')],
                       prevent_initial_call=True)
    def toggle_download_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @dash_app.callback(Output('vis_dl_button', 'children'),
                       Input('vis_save_button', 'n_clicks'),
                       [State('vis_dl_checkbox', 'value'),
                        State('vis_path_input', 'value')],
                       prevent_initial_call=True)
    def download_data(click, value, path):
        data_list = [sc.data['interp_gravity']['target'],
                     sc.data['interp_gravity']['full'],
                     sc.data['interp_gravity']['raw'],
                     sc.data['perfect_gravity']['target'],
                     sc.data['perfect_gravity']['full'],
                     sc.data['noisy_gravity']['full'],
                     sc.data['perfect_gravity']['terrain'],
                     sc.data['perfect_gravity']['dem'],
                     sc.corrections['free_air'],
                     sc.corrections['terrain'],
                     sc.data['elevation']['terrain'],
                     sc.data['elevation']['dem'],
                     sc.data['corrected_gravity']['full'],
                     sc.data['corrected_gravity']['interp']]
        label_list = ['Interp_Only_Target_Signal',
                      'Interp_Target_Terrain_no_noise',
                      'Interp_Target_Terrain_with_noise',
                      'Full_Only_Target_Signal',
                      'Full_Target_Terrain_no_noise',
                      'Full_Target_Terrain_with_noise',
                      'True_Terrain_Gravity_Component',
                      'DTM_Gravity_Component',
                      'Free_Air_Correction',
                      'Terrain_Correction',
                      'True_Terrain_Elevation',
                      'DTM_Elevation',
                      'Full_Target_Terrain_corrected'
                      'Interp_Target_Terrain_corrected']

        for i in value:
            file_data = data_list[i][3]
            label = label_list[i]
            np.savetxt('{}{}.txt'.format(path, label), file_data)
            # add first part of a name
        return 'test'

    # Callback for switching pages within the dashboard.
    @dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname in ["/dashapp/", "/dashapp/page-1"]:
            return target_layout
        elif pathname == "/dashapp/page-2":
            return terrain_layout
        elif pathname == "/dashapp/page-3":
            return survey_layout
        elif pathname == "/dashapp/page-4":
            return vis_layout
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

    return dash_app.server
