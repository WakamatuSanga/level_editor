import bpy

# ブレンダーに登録するアドオン情報
bl_info = {
    "name": "レベルエディタ",
    "author": "Taro Kamata",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

import bpy

# アドオン情報

# 1. メニュー項目描画関数
def draw_menu_manual(self, context):
    # self : 呼び出し元のクラスインスタンス。C++でいうthisポインタ
    # context : カーソルを合わせた時のポップアップのカスタマイズなどに使用
    
    # トップバーの「エディターメニュー」に項目（オペレータ）を追加
    self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

# 2. サブメニュークラスの定義
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # Blenderがクラスを識別するための固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    # 著者表示用の文字列
    bl_description = "拡張メニュー by " + bl_info.get("author", "Unknown")

    # サブメニュー内の描画（draw_menu_manual相当）
    def draw(self, context):
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        # 区切り線
        self.layout.separator()
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')
        # 区切り線
        self.layout.separator()
        self.layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

    # 既存のメニューにサブメニューを追加するための関数
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 3. 登録するクラスのリスト
classes = (
    TOPBAR_MT_my_menu,
)

# 4. 有効化・無効化時の処理
def register():
    # Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # メニューに項目を追加（サブメニューをトップバーに追加）
    # bpy.types.TOPBAR_MT_editor_menus がトップバーのクラス名
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました。")

def unregister():
    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    
    # Blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")

if __name__ == "__main__":
    register()