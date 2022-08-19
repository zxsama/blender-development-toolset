import os
import time
import bpy
import numpy as np
from math import ceil, floor
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
        flow = col.grid_flow(columns=2, align=True)
        flow.prop(custom_prop, 'subpix_size_x', text="X subsize")
        flow.prop(custom_prop, 'subpix_size_y', text="Y subsize")

        flow = col.grid_flow(columns=2, align=True)
        flow.prop(scene, 'frame_start', text="start")
        flow.prop(scene, 'frame_end', text="end")
                
        flow = col.grid_flow(columns=0, align=True)
        flow.scale_y = 1.5
        flow.operator(MZ_OT_MergeRenderResultResponsive.bl_idname, text="合并输出", icon='RENDER_ANIMATION')
          
        
# class MZ_OT_MergeRenderResult(bpy.types.Operator):
#     bl_idname = "mz.merge_render_result"
#     bl_label = "merge render result"
#     bl_description = '渲染并合并序列帧为一张图'
#     bl_options = {'REGISTER'}
    
#     # subpix_size_y: bpy.props.IntProperty(
#     #     name='subpix_size_y',
#     #     description="单张图片裁剪大小",
#     #     default=130,
#     #     min=0,
#     # )
    
#     def getboundingrect(self, gary_img, cv2):
#         """获取传入灰度图像的边界
        
#         :param gary_img: 灰度图
#         :param cv2: api
#         :return: 边界左上角(x, y), 长宽(w, h)
#         """
#         contours, _ = cv2.findContours(gary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         x, y, w, h = 0,0,0,0
#         for cnt in contours:
#             tmp_x, tmp_y, tmp_w, tmp_h = cv2.boundingRect(cnt)
#             if tmp_w>w and tmp_h>h:
#                 x, y, w, h = tmp_x, tmp_y, tmp_w, tmp_h
#         return x, y, w, h
    
#     def invoke(self, context, event):
#         bpy.ops.render.render(animation=True)
#         try:
#             import cv2
#         except ImportError:
#             install_modul(self, "opencv-python")
#         scene = context.scene
#         custom_prop = scene.mz_custom_prop
#         filepath = bpy.path.abspath(scene.render.filepath)
#         filepath = os.path.abspath(filepath)
        
#         pics = os.listdir(filepath)
#         subpix_size_y = custom_prop.subpix_size_y
#         result_pic = np.zeros((subpix_size_y, 0, 4), np.uint8)
        
#         for pic in pics:
#             pic_path = os.path.join(filepath, pic)
#             print(pic_path)
#             # img = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)
#             img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED) # 用于支持中文路径
#             if len(cv2.split(img)) > 3:
#                 b, g, r, a = cv2.split(img)
#                 img_gray = a.astype(np.uint8)
#             else:
#                 self.report({'WARNING'}, "no alpha")
#                 return {'FINISHED'}
#                 # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#                 # TODO:
                
#             x, y, w, h = self.getboundingrect(img_gray, cv2)
#             img = img[y:y+h, x:x+w]
#             border_y = (subpix_size_y - h)/2
#             border_x = (subpix_size_y - w)/2
#             if subpix_size_y<h or subpix_size_y<w:
#                 self.report({'WARNING'}, "merge size less than {bsize}.".format(bsize=max(h,w)))
#                 return {'FINISHED'}
#             img = cv2.copyMakeBorder(img,
#                                     int(ceil(border_y)),
#                                     int(floor(border_y)),
#                                     int(ceil(border_x)),
#                                     int(floor(border_x)),
#                                     cv2.BORDER_CONSTANT,
#                                     value=[0,0,0,0]
#                                     )
#             result_pic = cv2.hconcat([result_pic,img])
            
#         ftime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
#         tar_redr = os.path.dirname(filepath)
#         tar_redr = os.path.join(tar_redr, "comp_"+ftime+".png")
#         # cv2.imwrite(tar_redr,result_pic)
#         cv2.imencode('.png', result_pic)[1].tofile(tar_redr) # 用于支持中文路径
        
#         return self.execute(context)
    
#     def execute(self, context):
#         return {'FINISHED'}
    
    
class MZ_OT_MergeRenderResultResponsive(bpy.types.Operator):
    bl_idname = "mz.merge_render_result_responsive"
    bl_label = "merge render result"
    bl_description = '渲染并合并序列帧为一张图(响应式)'
    bl_options = {'REGISTER'}
    
    # Define some variables to register
    _timer = None
    shots = None
    stop = None
    rendering = None
    
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
    
    def merge_img(self, scene, context=None):    
        self.cancelled(scene)    
        
        try:
            import cv2
        except ImportError:
            install_modul(self, "opencv-python")
        custom_prop = scene.mz_custom_prop
        filepath = bpy.path.abspath(scene.render.filepath)
        filepath = os.path.abspath(filepath)
        
        pics = os.listdir(filepath)
        subpix_size_y = custom_prop.subpix_size_y
        subpix_size_x = custom_prop.subpix_size_x
        result_pic = np.zeros((subpix_size_y, 0, 4), np.uint8)
        
        for pic in pics:
            pic_path = os.path.join(filepath, pic)
            # img = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED) # 用于支持中文路径
            if len(cv2.split(img)) > 3:
                b, g, r, a = cv2.split(img)
                img_gray = a.astype(np.uint8)
            else:
                self.report({'WARNING'}, "no alpha")
                return {'FINISHED'}
                # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # TODO:
                
            x, y, w, h = self.getboundingrect(img_gray, cv2)
            
            info_report = False
            if subpix_size_y<h:
                self.report({'WARNING'}, "subpixel size y less than {bsize}.".format(bsize=h))
                info_report = True
            elif subpix_size_x<w:
                self.report({'WARNING'}, "subpixel size x less than {bsize}.".format(bsize=w))
                info_report = True
            if info_report:
                return {'FINISHED'}

            img = img[y:y+h, x:x+w]
            border_y = (subpix_size_y - h)/2
            border_x = (subpix_size_x - w)/2
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
        # cv2.imwrite(tar_redr,result_pic)
        cv2.imencode('.png', result_pic)[1].tofile(tar_redr) # 用于支持中文路径
        self.report({'INFO'}, "Merge save as {path}".format(path=tar_redr))
        
    # Define the handler functions. I use pre and
    # post to know if Blender "is rendering"
    def pre(self, scene, context=None):
        self.rendering = True
        
    def post(self, scene, context=None):
        # self.shots.pop(0) # This is just to render the next
                          # image in another path
        self.rendering = False

    def cancelled(self, scene, context=None):
        self.stop = True

    def execute(self, context):
        # Define the variables during execution. This allows
        # to define when called from a button
        self.stop = False
        self.rendering = False
                
        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)
        bpy.app.handlers.render_complete.append(self.merge_img)
        
        # The timer gets created and the modal handler
        # is added to the window manager
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        return {"RUNNING_MODAL"}
        
    def modal(self, context, event):
        if event.type == 'TIMER': # This event is signaled every half a second
                                  # and will start the render if available
            
            # If cancelled or no more shots to render, finish.
            if self.stop is True: 
                
                # We remove the handlers and the modal timer to clean everything
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                bpy.app.handlers.render_complete.remove(self.merge_img)
                context.window_manager.event_timer_remove(self._timer)
                
                return {"FINISHED"} # I didn't separate the cancel and finish
                                    # events, because in my case I don't need to,
                                    # but you can create them as you need
            
            elif self.rendering is False: # Nothing is currently rendering.
                                          # Proceed to render.
                bpy.ops.render.render("INVOKE_DEFAULT", animation=True)

        return {"PASS_THROUGH"}
        # This is very important! If we used "RUNNING_MODAL", this new modal function
        # would prevent the use of the X button to cancel rendering, because this
        # button is managed by the modal function of the render operator,
        # not this new operator!