import bpy

class MZ_CustomProps(bpy.types.PropertyGroup):
    
    subpix_size_y: bpy.props.IntProperty(
        name="subpix_size_y",
        description="单张图片裁剪大小y",
        default=130,
        min=0,
    )
    
    subpix_size_x: bpy.props.IntProperty(
        name="subpix_size_y",
        description="单张图片裁剪大小x",
        default=130,
        min=0,
    )
    
    def update_global_float_param_01(self, context):
        mats = bpy.data.materials
        scene = context.scene
        param_01_name = scene.mz_custom_prop.global_param_01_name
        for mat in mats:
            nodetree = mat.node_tree
            if nodetree:
                nodes = nodetree.nodes
                node = nodes.get(param_01_name)
                if node:
                    node.outputs[0].default_value = self.global_float_param_01
    
    global_float_param_01: bpy.props.FloatProperty(
        name="global_float_param_01",
        description="材质全局参数01",
        default=0.0,
        update=update_global_float_param_01,
    )
    
    global_param_01_name: bpy.props.StringProperty(
        name="global_param_01_name", 
        default="", 
        description="材质全局参数01的名称",
    )
    
    def update_get_nodegrp_property_type(self, context):
        custom_prop = context.scene.mz_custom_prop
        nodegrp_name = custom_prop.used_nodegrp_name
        nodegrp = bpy.data.node_groups.get(nodegrp_name)
        if nodegrp:
            input = nodegrp.inputs.get(self.nodegrp_property_name)
            if input:
                custom_prop.nodegrp_value_type = input.type
            else:
                custom_prop.nodegrp_value_type = ""
                
    def update_reset_attribute(self, context):
        custom_prop = context.scene.mz_custom_prop
        custom_prop.nodegrp_property_name = ""
        custom_prop.nodegrp_value_type = ""
         
    used_nodegrp_name: bpy.props.StringProperty(
        name="used_nodegroup",
        default="",
        description="用于属性修改的节点组名称",
        update=update_reset_attribute,
    )
    replace_nodegrp_name: bpy.props.StringProperty(
        name="used_nodegroup",
        default="",
        description="用于节点替换的节点组名称",
    )    
    nodegrp_property_name: bpy.props.StringProperty(
        name="used_nodegroup",
        default="",
        description="节点组中修改的属性名称",
        update=update_get_nodegrp_property_type,
    )
    nodegrp_value_type: bpy.props.StringProperty(
        name="nodegrp_value_type",
        description="节点组中修改的属性值类型",
        default="",
    )
    nodegrp_value_float: bpy.props.FloatProperty(
        name="nodegrp_value_float",
        description="节点组属性类型(float)",
        default=.0,
    )
    nodegrp_value_vector: bpy.props.FloatVectorProperty(
        name="nodegrp_value_vector",
        description="节点组属性类型(vector)",
        default=(.0,.0,.0),
        size=3,
        subtype="XYZ",
    )
    nodegrp_value_color: bpy.props.FloatVectorProperty(
        name="nodegrp_value_color",
        description="节点组属性类型(color)",
        default=(.0,.0,.0,1.0),
        size=4,
        subtype="COLOR",
    )