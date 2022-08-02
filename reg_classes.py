from .tool_bar import (UI_OT_Switch_ZH_EN,
                       UI_OT_OpenAddonPath,
                       UI_OT_ReloadAddon,
                       UI_OT_RestartBlender,
                       UI_OT_RestartSavedBlender,
                       UI_OT_ConsoleToggle,
                       )

from .material_show_panel import (MAT_PT_MaterialShow,
                                  )

from .merge_render import(MZ_PT_MergeRender,
                          MZ_OT_MergeRenderResult,
                          )
from .custom_props import MZ_CustomProps

from .preferences import MZ_Preferences

all_classes = [
    UI_OT_Switch_ZH_EN,
    UI_OT_OpenAddonPath,
    UI_OT_ReloadAddon,
    UI_OT_RestartBlender,
    UI_OT_RestartSavedBlender,
    UI_OT_ConsoleToggle,

    MZ_CustomProps,
    MZ_Preferences,
    
    MAT_PT_MaterialShow,
    
    MZ_PT_MergeRender,
    MZ_OT_MergeRenderResult,
]

bar_classes = [
    UI_OT_Switch_ZH_EN,
    UI_OT_OpenAddonPath,
    UI_OT_ReloadAddon,
    UI_OT_RestartBlender,
    UI_OT_RestartSavedBlender,
    UI_OT_ConsoleToggle,
]
