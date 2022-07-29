from math import ceil, floor
import os
import time
import bpy
import numpy as np
from .functions import install_modul


class MZ_PT_MergeRender(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MZ Toolset'
    bl_label = '合并输出'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    def draw(self, context):
        scene = context.scene
        custom_prop = scene.mz_custom_prop
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        
        col = layout.column(align=True)        
        flow = col.grid_flow(columns=0, align=True)
        flow.prop(scene.render, 'filepath', text="")
        flow.prop(custom_prop, 'single_pix_size', text="merge size")

        flow = col.grid_flow(columns=2, align=True)
        flow.prop(scene, 'frame_start', text="start")
        flow.prop(scene, 'frame_end', text="end")
                
        flow = col.grid_flow(columns=0, align=True)
        flow.scale_y = 1.5
        meg_rend = flow.operator(MZ_OT_MergeRenderResult.bl_idname, text="合并输出", icon='RENDER_ANIMATION')
        meg_rend.single_pix_size = custom_prop.single_pix_size
        
        
class MZ_OT_MergeRenderResult(bpy.types.Operator):
    bl_idname = "mz.merge_render_result"
    bl_label = "merge render result"
    bl_description = '渲染并合并序列帧为一张图'
    bl_options = {'REGISTER'}
    
    single_pix_size: bpy.props.IntProperty(
        name='single_pix_size',
        description="单张图片裁剪大小",
        default=130,
        min=0,
    )
    
    def getboundingrect(self, gary_img, cv2):
        """获取传入灰度图像的边界
        
        :param gary_img: 灰度图
        :param cv2: api
        :return: 边界左上角(x, y), 长宽(w, h)
        """
        contours, _ = cv2.findContours(gary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = 0,0,0,0
        for cnt in contours:
            tmp_x, tmp_y, tmp_w, tmp_h = cv2.boundingRect(cnt)
            if tmp_w>w and tmp_h>h:
                x, y, w, h = tmp_x, tmp_y, tmp_w, tmp_h
        return x, y, w, h
    
    def invoke(self, context, event):
        try:
            import cv2
        except ImportError:
            install_modul("opencv-python")
        bpy.ops.render.render(animation=True)
        scene = context.scene
        filepath = bpy.path.abspath(scene.render.filepath)
        filepath = os.path.abspath(filepath)
        
        pics = os.listdir(filepath)
        self.single_pix_size = 130
        result_pic = np.zeros((self.single_pix_size, 0, 4), np.uint8)
        
        for pic in pics:
            pic_path = os.path.join(filepath, pic)
            print(pic_path)
            img = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)
            if len(cv2.split(img)) > 3:
                b, g, r, a = cv2.split(img)
                img_gray = a.astype(np.uint8)
            else:
                self.report({'WARINING'}, "no alpha")
                return {'FINISHED'}
                # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # TODO:
                
            x, y, w, h = self.getboundingrect(img_gray, cv2)
            img = img[y:y+h, x:x+w]
            border_y = (self.single_pix_size - h)/2
            border_x = (self.single_pix_size - w)/2
            if self.single_pix_size<h or self.single_pix_size<w:
                self.report({'WARINING'}, "too small in size.")
                return {'FINISHED'}
            img = cv2.copyMakeBorder(img,
                                    int(ceil(border_y)),
                                    int(floor(border_y)),
                                    int(ceil(border_x)),
                                    int(floor(border_x)),
                                    cv2.BORDER_CONSTANT,
                                    value=[0,0,0,0]
                                    )
            result_pic = cv2.hconcat([result_pic,img])
            
        ftime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        tar_redr = os.path.dirname(filepath)
        tar_redr = os.path.join(tar_redr, "comp_"+ftime+".png")
        cv2.imwrite(tar_redr,result_pic)
        
        return self.execute(context)
    
    def execute(self, context):
        return {'FINISHED'}