import bpy
from bpy_extras.node_utils import find_node_input


class MAT_PT_MaterialShow(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MZ Toolset'
    bl_label = '材质参数'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):

        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        col = layout.column(align=True)
        # flow = col.grid_flow(columns=0, align=True)
        scene = context.scene
        dev_prop = scene.mz_custom_prop
        row = col.row(align=True)
        row.prop(dev_prop, 'global_param_01_name',text="")
        row.prop(dev_prop, 'global_float_param_01', text="")
        
        
        obj = context.object

        if obj:
            mat_slots = obj.material_slots
            for slot in mat_slots:
                mat = slot.material
                slot_label = "{obj_name} | {mat_name} | slot{slidx}".format(
                    obj_name=obj.name, mat_name=mat.name, slidx=slot.slot_index)
                col.label(text=slot_label)
                flow_val = col.grid_flow(columns=0, align=True)
                flow_rgb = col.grid_flow(columns=0, align=True)
                flow_rgb_curve = col.grid_flow(columns=0, align=True)
                if mat:
                    ntree = mat.node_tree
                    nodes = ntree.nodes
                    for node in nodes:
                        if node.label:
                            if node.type in {'VALUE'}:
                                flow_val.prop(
                                    node.outputs[0], 'default_value', text=node.label)
                            elif node.type in {'RGB'}:
                                flow_rgb.prop(
                                    node.outputs[0], 'default_value', text=node.label)
                            elif node.type in {'CURVE_RGB'}:
                                # input = find_node_input(node, 'Surface')
                                # flow_rgb_curve.template_node_view(ntree, node, input)
                                flow_rgb_curve.label(text=node.label)
                                flow_rgb_curve.template_curve_mapping(
                                    node, 'mapping', type='COLOR')
