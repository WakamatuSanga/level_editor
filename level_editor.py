import bpy
import json
import os
import math
from bpy_extras.io_utils import ExportHelper

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

def write_and_print(file, str):
    """コンソールとファイルに同時出力する関数
    
    Args:
        file: ファイルハンドル
        str: 出力文字列
    """
    print(str)
    file.write(str)


def parse_scene_recursive(file, object, level):
    """シーン構造を再帰的に処理する関数
    
    Args:
        file: ファイルハンドル
        object: 処理対象オブジェクト
        level: インデントレベル (深さ)
    """
    # インデント文字列を生成（レベルごとに4つのスペース）
    indent = "    " * level
    
    # オブジェクト情報を出力
    write_and_print(file, indent + object.type + " - " + object.name + "\n")
    
    # ローカルトランスフォーム行列から平行移動、回転、スケーリングを抽出
    # 型は Vector, Quaternion, Vector
    trans, rot_quat, scale = object.matrix_local.decompose()
    
    # 回転を Quaternion から Euler (3軸での回転角) に変換
    rot = rot_quat.to_euler()
    
    # ラジアンから度数法に変換
    rot.x = math.degrees(rot.x)
    rot.y = math.degrees(rot.y)
    rot.z = math.degrees(rot.z)
    
    # トランスフォーム情報を整形して出力
    write_and_print(file, indent + "Trans(%f,%f,%f)\n" % (trans.x, trans.y, trans.z))
    write_and_print(file, indent + "Rot(%f,%f,%f)\n" % (rot.x, rot.y, rot.z))
    write_and_print(file, indent + "Scale(%f,%f,%f)\n" % (scale.x, scale.y, scale.z))
    
    # カスタムプロパティ 'file_name' がある場合は出力
    if "file_name" in object:
        write_and_print(file, indent + "N %s" % object["file_name"] + "\n")
    
    write_and_print(file, indent + "END\n")
    
    # ルート直下のオブジェクトのみでfor文で処理する
    # （子オブジェクトは再帰関数で処理するため）
    for child in object.children:
        # シーン内にある子オブジェクトについて、同じ関数で処理する（再帰呼び出し）
        parse_scene_recursive(file, child, level + 1)


class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "ファイル名を追加"
    bl_description = "オブジェクトにファイル名というカスタムプロパティを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # 今選択中のオブジェクトに 'file_name' というカスタムプロパティを追加
        context.object["file_name"] = ""
        
        return {'FINISHED'}


class MYADDON_OT_export_scene(bpy.types.Operator, ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"
    
    filename_ext = ".scene"
    filter_glob: bpy.props.StringProperty(
        default="*.scene",
        options={'HIDDEN'}
    )

    def execute(self, context):
        print("シーン情報をExportします")
        
        # ファイルディレクトリが存在しない場合は作成
        save_dir = os.path.dirname(self.filepath)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        
        # ファイルを開いて書き込み
        with open(self.filepath, 'w') as file:
            # シーン内でルート階層（親がない）のオブジェクトのみを走査
            # ページで追加されたオブジェクト情報表示の処理を
            # exportの with ブロック内に差し込む。
            for object in bpy.context.scene.objects:
                # 親がないオブジェクト（ルート階層）のみを処理対象にする
                if object.parent:
                    continue
                # その後 print() だった部分を
                # file.write() に置き換える。
                parse_scene_recursive(file, object, 0)
        
        self.report({'INFO'}, "シーン情報をExportしました")
        print("シーン情報をExportしました")
        
        return {'FINISHED'}

# 2. Panelクラスの定義
class OBJECT_PT_file_name(bpy.types.Panel):
    bl_label = "FileName"
    bl_idname = "OBJECT_PT_file_name"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        
        # パネルに登録する条件
        if "file_name" in context.object:
            # プロパティを表示
            layout.prop(context.object, '["file_name"]', text=self.bl_label)
        else:
            # プロパティがない場合、オペレータ追加ボタンを表示
            layout.operator(MYADDON_OT_add_filename.bl_idname)

# 3. メニュークラスの定義
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "拡張メニュー by " + bl_info.get("author", "Unknown")

    def draw(self, context):
        layout = self.layout
        # 自作オペレーターをメニューに登録
        layout.operator(MYADDON_OT_create_ico_sphere.bl_idname, text="ICO球を作成", icon='MESH_UVSPHERE')
        layout.operator(WM_OT_level_export.bl_idname, text="Level Export", icon='EXPORT')
        layout.operator(MYADDON_OT_export_scene.bl_idname, icon='EXPORT')
        layout.operator(MYADDON_OT_add_filename.bl_idname, icon='FILE')
        layout.separator()
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 4. クラスリストの更新
classes = (
    MYADDON_OT_create_ico_sphere,
    WM_OT_level_export,
    MYADDON_OT_add_filename,
    MYADDON_OT_export_scene,
    OBJECT_PT_file_name,
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