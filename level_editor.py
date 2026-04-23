import bpy
import json
import os

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
# アドオン情報

# 1. カスタムオペレーターの定義
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object"
    bl_label = "ICO球を作成します"
    bl_description = "ICO球を作成します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を作成しました。")
        
        return {'FINISHED'}

class WM_OT_level_export(bpy.types.Operator):
    bl_idname = "wm.level_export"
    bl_label = "Level Export"
    bl_description = "レベルデータをJSON形式で書き出します"

    def execute(self, context):
        # シリアル化のメイン処理
        print("レベルエクスポートを実行します")
        
        # 保存用リスト
        data_list = []
        
        # シーン内の全てのオブジェクトを走査
        for obj in bpy.context.scene.objects:
            # 辞書形式でデータを抽出
            data = {
                "name": obj.name,
                "type": obj.type,
                "location": {
                    "x": obj.location.x,
                    "y": obj.location.y,
                    "z": obj.location.z
                }
            }
            data_list.append(data)
        
        # ファイルへの書き出し処理
        save_path = "C:/Users/K024G/Desktop/level_data/level_data.json"
        # ディレクトリが存在しない場合は作成
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4)
            
        self.report({'INFO'}, f"保存完了: {save_path}")
        return {'FINISHED'}

# 2. メニュークラスの定義
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "拡張メニュー by " + bl_info.get("author", "Unknown")

    def draw(self, context):
        layout = self.layout
        # 自作オペレーターをメニューに登録
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text="ICO球を作成", icon='MESH_UVSPHERE')
        layout.operator(WM_OT_level_export.bl_idname, text="Level Export", icon='EXPORT')
        layout.separator()
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 3. クラスリストの更新
classes = (
    MYADDON_OT_create_ico_sphere,
    WM_OT_level_export,
    TOPBAR_MT_my_menu,
)

# 4. 登録・解除処理
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("レベルエディタが有効化されました。")

def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")

if __name__ == "__main__":
    register()