import bpy
from bpy_extras.node_utils import find_node_input
from re import findall
from .functions import collection_search

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
        custom_prop = scene.mz_custom_prop
        
        # 节点组批量替换与属性修改(仅shader)
        sub_box = col.box()
        sub_flow = sub_box.grid_flow(columns=0, align=True)
        sub_flow.use_property_split = True
        sub_flow.label(text="节点组批量替换与属性修改(仅shader)")
        sub_flow.prop(custom_prop, "used_nodegrp_name", text="Node Group")
        
        sub_flow = sub_box.box()
        sub_flow.label(text="Attribute Name:")
        sub_flow.prop(custom_prop, "nodegrp_property_name", text="")
        grp_type = custom_prop.nodegrp_value_type
        value_text = custom_prop.nodegrp_property_name + " Value:"
        sub_flow.label(text=value_text)
        if grp_type == "VALUE":
            sub_flow.prop(custom_prop, "nodegrp_value_float", text="")
        elif grp_type == "VECTOR":
            sub_flow.prop(custom_prop, "nodegrp_value_vector", text="")
        elif grp_type == "RGBA":
            sub_flow.prop(custom_prop, "nodegrp_value_color", text="")
        sub_flow = sub_flow.grid_flow(columns=0, align=True)
        sub_flow.scale_y = 1.5
        sub_flow.operator(MZ_OT_ChangeNodegroupProperty.bl_idname, text="全局修改")
        
        sub_flow = sub_box.box()
        sub_flow = sub_flow.grid_flow(columns=0, align=True)
        sub_flow.label(text="Repalce NodeGroup Name:")
        sub_flow.prop(custom_prop, "replace_nodegrp_name", text="")
        sub_flow = sub_flow.grid_flow(columns=0, align=True)
        sub_flow.scale_y = 1.5
        sub_flow.operator(MZ_OT_ReplaceNodegroup.bl_idname, text="全局替换")
        
        # 材质内属性批量修改(仅value)
        sub_box = col.box()
        sub_flow = sub_box.box()
        sub_flow.label(text="材质内属性批量修改(仅value)")
        sub_flow = sub_flow.row(align=True)
        sub_flow.prop(custom_prop, 'global_param_01_name', text="")
        sub_flow.prop(custom_prop, 'global_float_param_01', text="")

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


class MZ_OT_ChangeNodegroupProperty(bpy.types.Operator):
    bl_idname = "mz.change_nodegroup_property"
    bl_label = "change nodegroup property"
    bl_description = '统一修改nodegroup中的属性值'
    bl_options = {'REGISTER', 'UNDO'}
    
    changed_count: bpy.props.IntProperty(
        name="changed_count",
        description="修改的节点计数",
        default=0,
    )
    
    def change_nodegrp_attribute(self, nodes, nodegrp, property_name, value):
        for node in nodes:
            if node.type=="GROUP" and node.node_tree.name==nodegrp.name:
                node.inputs[property_name].default_value = value
                self.changed_count += 1
        
    @classmethod
    def poll(cls, context):
        custom_prop = context.scene.mz_custom_prop
        nodegrp_name = custom_prop.used_nodegrp_name
        grp_value_type = custom_prop.nodegrp_value_type
        nodegrp = bpy.data.node_groups.get(nodegrp_name)
        if nodegrp and (not grp_value_type==""):
            return True
        else:
            return False

    def invoke(self, context, event):
        scene = context.scene
        custom_prop = scene.mz_custom_prop
        nodegrp_name = custom_prop.used_nodegrp_name
        property_name = custom_prop.nodegrp_property_name
        nodegrp = bpy.data.node_groups.get(nodegrp_name)
        if not nodegrp:
            self.report({"WARNING"}, "invalid nodegroup name")
            return {'CANCELLED'}
        if not nodegrp.type=="SHADER":
            self.report({"WARNING"}, "only shader nodegroup")
            return {'CANCELLED'}
            
        grp_type = custom_prop.nodegrp_value_type
        if grp_type == "VALUE":
            gvalue = custom_prop.nodegrp_value_float
        elif grp_type == "VECTOR":
            gvalue = custom_prop.nodegrp_value_vector
        elif grp_type == "RGBA":
            gvalue = custom_prop.nodegrp_value_color
            
        # 批量修改
        for users in collection_search(nodegrp):
            block_name = findall(r"data.(.*?)\[", users[0])
            block_name = block_name[0]
            nodes = None
            if block_name == "materials":
                for mat_data in users:
                    data_name = mat_data[20:-2]
                    mat = bpy.data.materials[data_name]
                    nodes = mat.node_tree.nodes
                    self.change_nodegrp_attribute(nodes, nodegrp, property_name, gvalue)
            elif block_name == "node_groups":
                for grp_data in users:
                    data_name = grp_data[22:-2]
                    grp = bpy.data.node_groups[data_name]
                    nodes = grp.nodes
                    self.change_nodegrp_attribute(nodes, nodegrp, property_name, gvalue)
            elif block_name == "worlds":
                for world_data in users:
                    data_name = world_data[17:-2]
                    world = bpy.data.worlds[data_name]
                    nodes = world.node_tree.nodes
                    self.change_nodegrp_attribute(nodes, nodegrp, property_name, gvalue)
            else:
                self.report({"WARNING"}, "not supported block: "+block_name+str(users))

        return self.execute(context)

    def execute(self, context):
        self.report({"INFO"}, "Changed: "+str(self.changed_count))
        self.changed_count = 0
        return {'FINISHED'}

class MZ_OT_ReplaceNodegroup(bpy.types.Operator):
    bl_idname = "mz.replace_nodegroup"
    bl_label = "replace nodegroup"
    bl_description = '统一替换全局的nodegroup'
    bl_options = {'REGISTER', 'UNDO'}
    
    changed_count: bpy.props.IntProperty(
        name="changed_count",
        description="修改的节点计数",
        default=0,
    )
    
    def repalce_nodegrp(self, nodes, nodegrp, replace_grp):
        for node in nodes:
            if node.type=="GROUP" and node.node_tree.name==nodegrp.name:
                node.node_tree = replace_grp
                self.changed_count += 1
    
    @classmethod
    def poll(cls, context):
        custom_prop = context.scene.mz_custom_prop
        grp_name = custom_prop.used_nodegrp_name
        replace_grp_name = custom_prop.replace_nodegrp_name
        nodegrp = bpy.data.node_groups.get(grp_name)
        replace_grp = bpy.data.node_groups.get(replace_grp_name)
        if nodegrp and replace_grp:
            return True
        else:
            return False
        
    def invoke(self, context, event):
        scene = context.scene
        custom_prop = scene.mz_custom_prop
        grp_name = custom_prop.used_nodegrp_name
        replace_grp_name = custom_prop.replace_nodegrp_name
        nodegrp = bpy.data.node_groups.get(grp_name)
        replace_grp = bpy.data.node_groups.get(replace_grp_name)
        
        # 批量替换
        for users in collection_search(nodegrp):
            block_name = findall(r"data.(.*?)\[", users[0])
            block_name = block_name[0]
            nodes = None
            if block_name == "materials":
                for mat_data in users:
                    data_name = mat_data[20:-2]
                    mat = bpy.data.materials[data_name]
                    nodes = mat.node_tree.nodes
                    self.repalce_nodegrp(nodes, nodegrp, replace_grp)
            elif block_name == "node_groups":
                for grp_data in users:
                    data_name = grp_data[22:-2]
                    grp = bpy.data.node_groups[data_name]
                    nodes = grp.nodes
                    self.repalce_nodegrp(nodes, nodegrp, replace_grp)
            elif block_name == "worlds":
                for world_data in users:
                    data_name = world_data[17:-2]
                    world = bpy.data.worlds[data_name]
                    nodes = world.node_tree.nodes
                    self.repalce_nodegrp(nodes, nodegrp, replace_grp)
            else:
                self.report({"WARNING"}, "not supported block: "+block_name+str(users))
        
        return self.execute(context)
    
    def execute(self, context):
        self.report({"INFO"}, "Changed: "+str(self.changed_count))
        self.changed_count = 0
        return {'FINISHED'}