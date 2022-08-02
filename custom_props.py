import bpy
from .tool_bar import bar_button

class MZ_CustomProps(bpy.types.PropertyGroup):
    
    single_pix_size: bpy.props.IntProperty(
        name='single_pix_size',
        description="单张图片裁剪大小",
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
        name='global_float_param_01',
        description='材质全局参数01',
        default=0.0,
        update=update_global_float_param_01,
    )
    
    global_param_01_name: bpy.props.StringProperty(
        name="global_param_01_name", 
        default="", 
        description="材质全局参数01的名称"
    )
    
    def update_bar_ops(self, context):
        for index, (cls, _) in enumerate(bar_button.items()):
            if not self.enable_bar_buttons[index]:
                ...
                # TODO: unregist class
                
        
    enable_bar_buttons: bpy.props.BoolVectorProperty(
        name='enable_bar_buttons', 
        default=[True]*len(bar_button), 
        size=len(bar_button),
        # update=update_bar_ops,
    )