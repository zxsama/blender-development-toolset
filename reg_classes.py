from .bilingual_translator import (
    MZ_OT_GenerateBilingualTranslator,
    MZ_OT_RegisterBilingualTranslator,
    MZ_OT_OpenBilingualWhiteList,
)
from .tool_bar import (
    UI_OT_Switch_ZH_EN,
    UI_OT_OpenAddonPath,
    UI_OT_RestartBlender,
    UI_OT_RestartSavedBlender,
    UI_OT_ConsoleToggle,
    MZ_HT_BarUI,
)

from .material_show_panel import (
    MAT_PT_MaterialShow,
    MZ_OT_ChangeNodegroupProperty,
    MZ_OT_ReplaceNodegroup,
)

from .merge_render import (
    MZ_PT_MergeRender,
    MZ_OT_MergeRenderResultResponsive,
)
from .custom_props import (
    MZ_CustomProps,
    MZ_BilingualTranslatorProps,
)

from .preferences import MZ_Preferences

all_classes = [
    MZ_Preferences,
    MZ_CustomProps,
    MZ_BilingualTranslatorProps,
    MAT_PT_MaterialShow,
    MZ_PT_MergeRender,
    MZ_HT_BarUI,
    MZ_OT_MergeRenderResultResponsive,
    UI_OT_Switch_ZH_EN,
    UI_OT_OpenAddonPath,
    UI_OT_RestartBlender,
    UI_OT_RestartSavedBlender,
    UI_OT_ConsoleToggle,
    MZ_OT_ChangeNodegroupProperty,
    MZ_OT_ReplaceNodegroup,
    MZ_OT_GenerateBilingualTranslator,
    MZ_OT_RegisterBilingualTranslator,
    MZ_OT_OpenBilingualWhiteList,
]

bar_classes = [
    MZ_HT_BarUI,
]
