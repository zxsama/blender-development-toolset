from .bilingual_translator import (
    MZ_OT_GenerateBilingualTranslator,
    MZ_OT_RegisterBilingualTranslator,
    MZ_OT_OpenBilingualBlackWhiteList,
    MZ_OT_DeleteBilingualTranslator,
)
from .tool_bar import (
    UI_OT_Switch_Language,
    UI_OT_OpenAddonPath,
    UI_OT_RestartBlender,
    UI_OT_RestartSavedBlender,
    UI_OT_ConsoleToggle,
    MZ_HT_BarUI,
)
from .custom_props import (
    MZ_BilingualTranslatorProps,
)

from .preferences import MZ_Preferences

all_classes = [
    MZ_Preferences,
    MZ_BilingualTranslatorProps,
    MZ_HT_BarUI,
    UI_OT_Switch_Language,
    UI_OT_OpenAddonPath,
    UI_OT_RestartBlender,
    UI_OT_RestartSavedBlender,
    UI_OT_ConsoleToggle,
    MZ_OT_GenerateBilingualTranslator,
    MZ_OT_RegisterBilingualTranslator,
    MZ_OT_OpenBilingualBlackWhiteList,
    MZ_OT_DeleteBilingualTranslator,
]

bar_classes = [
    MZ_HT_BarUI,
]
