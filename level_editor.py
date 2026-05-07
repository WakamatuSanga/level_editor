import bpy
import copy
import gpu
from gpu_extras.batch import batch_for_shader
import json
import math
import mathutils
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

    if "collider" in object:
        write_and_print(file, indent + "C %s\n" % object["collider"])
        if "collider_center" in object:
            cc = object["collider_center"]
            write_and_print(file, indent + "CC %f %f %f\n" % (cc[0], cc[1], cc[2]))
        if "collider_size" in object:
            cs = object["collider_size"]
            write_and_print(file, indent + "CS %f %f %f\n" % (cs[0], cs[1], cs[2]))
    
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


class MYADDON_OT_add_collider(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_collider"
    bl_label = "コライダー追加"
    bl_description = "オブジェクトにコライダー用のカスタムプロパティを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # 今選択中のオブジェクトにコライダー情報のカスタムプロパティを追加
        context.object["collider"] = "BOX"
        context.object["collider_center"] = mathutils.Vector((0.0, 0.0, 0.0))
        context.object["collider_size"] = mathutils.Vector((2.0, 2.0, 2.0))
        
        return {'FINISHED'}


class MYADDON_OT_export_scene(bpy.types.Operator, ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    bl_description = "シーン情報をExportします"
    
    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )

    def export_json(self):
        json_object_root = dict()
        json_object_root["name"] = "scene"
        json_object_root["objects"] = list()

        for obj in bpy.context.scene.objects:
            if obj.parent:
                continue
            self.parse_scene_recursive_json(json_object_root["objects"], obj, 0)

        json_text = json.dumps(json_object_root, ensure_ascii=False, indent=4)
        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write(json_text)

    def parse_scene_recursive_json(self, data_parent, object, level):
        json_object = dict()
        json_object["type"] = object.type
        json_object["name"] = object.name

        trans, rot_quat, scale = object.matrix_local.decompose()
        rot = rot_quat.to_euler()
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)

        json_object["transform"] = {
            "translation": [trans.x, trans.y, trans.z],
            "rotation": [rot.x, rot.y, rot.z],
            "scaling": [scale.x, scale.y, scale.z],
        }

        if "file_name" in object:
            json_object["file_name"] = object["file_name"]

        if "collider" in object:
            collider = dict()
            collider["type"] = object["collider"]
            if "collider_center" in object:
                collider["center"] = list(object["collider_center"])
            if "collider_size" in object:
                collider["size"] = list(object["collider_size"])
            json_object["collider"] = collider

        if object.children:
            json_object["children"] = list()
            for child in object.children:
                self.parse_scene_recursive_json(json_object["children"], child, level + 1)

        data_parent.append(json_object)

    def execute(self, context):
        print("シーン情報をExportします")

        save_dir = os.path.dirname(self.filepath)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        self.export_json()

        self.report({'INFO'}, "シーン情報をExportしました")
        print("シーン情報をExportしました")

        return {'FINISHED'}

# 描画用クラス
class DrawCollider:
    handle = None

    @staticmethod
    def draw_collider():
        vertices = {"pos": []}
        indices = []

        offsets = [
            (-0.5, -0.5, -0.5),
            (0.5, -0.5, -0.5),
            (-0.5, 0.5, -0.5),
            (0.5, 0.5, -0.5),
            (-0.5, -0.5, 0.5),
            (0.5, -0.5, 0.5),
            (-0.5, 0.5, 0.5),
            (0.5, 0.5, 0.5),
        ]

        for obj in bpy.context.scene.objects:
            if "collider" not in obj:
                continue

            center = mathutils.Vector((0.0, 0.0, 0.0))
            size = mathutils.Vector((2.0, 2.0, 2.0))
            if "collider_center" in obj:
                center = mathutils.Vector(obj["collider_center"])
            if "collider_size" in obj:
                size = mathutils.Vector(obj["collider_size"])

            start = len(vertices["pos"])
            for offset in offsets:
                pos = center + mathutils.Vector(offset) * size
                pos = obj.matrix_world @ pos
                vertices["pos"].append(pos)

            indices.append((start + 0, start + 1))
            indices.append((start + 1, start + 3))
            indices.append((start + 3, start + 2))
            indices.append((start + 2, start + 0))
            indices.append((start + 4, start + 5))
            indices.append((start + 5, start + 7))
            indices.append((start + 7, start + 6))
            indices.append((start + 6, start + 4))
            indices.append((start + 0, start + 4))
            indices.append((start + 1, start + 5))
            indices.append((start + 2, start + 6))
            indices.append((start + 3, start + 7))

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', vertices, indices=indices)
        color = (0.5, 1.0, 1.0, 1.0)
        shader.bind()
        shader.uniform_float('color', color)
        batch.draw(shader)

# 2. Panelクラスの定義
class OBJECT_PT_file_name(bpy.types.Panel):
    bl_label = "FileName"
    bl_idname = "OBJECT_PT_file_name"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        
        if "file_name" in context.object:
            layout.prop(context.object, '["file_name"]', text="FileName")
        else:
            layout.operator(MYADDON_OT_add_filename.bl_idname)


class OBJECT_PT_collider(bpy.types.Panel):
    bl_label = "Collider"
    bl_idname = "OBJECT_PT_collider"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        
        if "collider" in context.object:
            layout.prop(context.object, '["collider"]', text="Type")
            layout.prop(context.object, '["collider_center"]', text="Center")
            layout.prop(context.object, '["collider_size"]', text="Size")
        else:
            layout.operator(MYADDON_OT_add_collider.bl_idname)

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
        layout.operator(MYADDON_OT_add_collider.bl_idname, icon='MESH_CUBE')
        layout.separator()
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# 4. クラスリストの更新
classes = (
    MYADDON_OT_create_ico_sphere,
    WM_OT_level_export,
    MYADDON_OT_add_filename,
    MYADDON_OT_add_collider,
    MYADDON_OT_export_scene,
    OBJECT_PT_file_name,
    OBJECT_PT_collider,
    TOPBAR_MT_my_menu,
)

# 4. 登録・解除処理
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), 'WINDOW', 'POST_VIEW')
    print("レベルエディタが有効化されました。")

def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    if DrawCollider.handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, 'WINDOW')
        DrawCollider.handle = None
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")

if __name__ == "__main__":
    register()